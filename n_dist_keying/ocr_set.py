from n_dist_keying.distance_storage import DistanceStorage
from n_dist_keying.text_comparator import TextComparator
from n_dist_keying.text_unspacer import TextUnspacer

class OCRset:
    """
        A storage class for a y_mean value
        and a set of lines which was assigned to each other
        If the lineset values where not edited, they are intialized with 'False
    """
    N_DISTANCE_SHORTEST_TAG = "n_distance_shortest"

    def __init__(self, lines_size, y_mean):
        lineset = []
        for x in range(0, lines_size):
            lineset.append(False)

        self._set_lines = lineset
        self._size = lines_size
        self._y_mean = y_mean
        self.d_storage = DistanceStorage()
        self.shortest_distance_line_index = -1
        self._unspaced = False # indicates the set_lines was unspaced

    def edit_line_set_value(self,set_index,new_value):
        self._set_lines[set_index] = new_value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size= value

    @property
    def y_mean(self):
        return self._y_mean

    @y_mean.setter
    def y_mean(self, value):
        self.y_mean = value

    def calculate_y_mean(self):
        """
        Goes through set elements and calculates y_mean for y_start and y_stop values
        :return:
        """

        acc_counter = 0
        y_start_final = 0
        y_stop_final = 0

        for line in self._set_lines:
            # don't count undefined values for means
            if line is False or line is None:
                continue
            # accumulate y-values
            (x_start, y_start, x_stop, y_stop) = line.coordinates
            y_start_final = y_start_final + y_start
            y_stop_final = y_stop_final + y_stop
            # add number of accumulation count
            acc_counter = acc_counter +1

        y_start_mean = y_start_final/acc_counter
        y_stop_mean = y_stop_final/acc_counter
        y_mean = (y_start_mean + y_stop_mean) / 2

        self._y_mean = round(y_mean)



    def is_full(self):
        """
        Checks if all lines are defined in the lineset
        :return: True or False
        """
        for line in self._set_lines:
            if line is False:
                return False

        return True

    def print_me(self, diff_only=False):

        lineset_acc=""
        one_line_is_false = False

        for line in self._set_lines:
            try:
                ocr_text = self.get_line_content(line)
                if ocr_text is False:
                    one_line_is_false = True
                    lineset_acc = lineset_acc+str(ocr_text)+"||"
                else:
                    lineset_acc = lineset_acc+ocr_text+"||"

            except:
                print("problem creating printable lineset ")

        lineset_acc = lineset_acc + "||"

        if diff_only is True:
            if one_line_is_false is True:
                print(str(self.y_mean) + "||"+str(self.shortest_distance_line_index)+"||" + lineset_acc)
        else:
            print(str(self.y_mean)+"||"+str(self.shortest_distance_line_index)+"||"+lineset_acc)



    def calculate_n_distance_keying(self):

        # do a line-wise comparison, which calculates a distance between all lines in this set
        for line_index, line in enumerate(self._set_lines):
            self.compare_with_other_lines(line_index,line)

        # calculate the distance from each item in set to all others
        for line_index, line in enumerate(self._set_lines):
            self.d_storage.calculate_accumulated_distance(line_index)

        # get the index of the item in set, which has the shortest distance to all others
        self.d_storage.calculate_shortest_distance_index()

        # save the result
        shortest_dist_index = self.d_storage.get_shortest_distance_index()
        self.shortest_distance_line_index = shortest_dist_index

    def get_shortest_n_distance_line(self):
        if self.shortest_distance_line_index >= 0:
            line = self._set_lines[self.shortest_distance_line_index]
            line_text = self.get_line_content(line)
            return line_text
        else:
            return None

    def print_shortest_n_distance_line(self):
        line = self.get_shortest_n_distance_line()
        if line is not None and line is not False:
            print(line)

    def compare_with_other_lines(self,line_index,line):
        ocr_text = self.get_line_content(line)

        for line_index_cmp, line_cmp in enumerate(self._set_lines):

            # if line has the same index, continue
            if line_index is line_index_cmp:
                continue

            existing_distance = self.d_storage.fetch_value(line_index, line_index_cmp)

            # if line was already compared, continue
            if existing_distance is not None:
                continue

            ocr_text_cmp = self.get_line_content(line_cmp)
            distance = self.get_distance(ocr_text, ocr_text_cmp)
            self.d_storage.store_value(line_index,line_index_cmp, distance)

    def get_distance(self, text1, text2):
        # todo add more possibilities for distance measurement, i.e confidences, edit distance, context weighting

        # return a fixed negative value if one of the strings is not defined
        if text1 is False and text2 is False:
            return 0

        # One is false and one is not false
        if text1 is False or text2 is False:
            return 1

        dist_one = TextComparator.compare_ocr_strings_difflib_seqmatch(text1, text2)
        return dist_one

    def get_line_content(self, line):
        """
        Helper method to get line content, because ocropus content
        has other access properties.
        :param line: line element to check upn
        :return: string with line content, or 'False if line isn't defined.
        """

        # hint: the attribute checked is created by hocr_line_normalizer
        if line is False:
            return False
        # elif hasattr(line, 'ocr_text_normalized'):
        elif line.ocr_text_normalized is not None:
            return line.ocr_text_normalized
        else:
            return line.ocr_text

    def unspace_lines(self):
        # todo make unspaced index adaptable
        unspaced_lines = TextUnspacer.unspace_texts(self._set_lines, 1)
        self._unspaced = True
        self._set_lines = unspaced_lines
