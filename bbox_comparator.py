"""
    https://github.com/athento/hocr-parser

"""

import os
from hocr_parser.parser import HOCRDocument,Line,Paragraph,Area
import difflib

def get_ocropus_boxes(filename):
    """
    Gets the box information for ocropus
    :param filename: name of the file to check for boxes
    :return: list of lines with boxes
    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dir_path, filename)
    document = HOCRDocument(full_path, is_path=True)
    page = document.pages[0]

    html = page._hocr_html
    contents = html.contents
    return_list = []
    for element in contents:
        res = str(element).find("span")
        if res>=1:
            liner = Line(document,element)
            return_list.append(liner)

    return return_list


ocrolist = get_ocropus_boxes("Testfiles/oneprof_ocropus.html")


def get_tesseract_boxes(filename):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dir_path, filename)
    document = HOCRDocument(full_path, is_path=True)
    page = document.pages[0]
    return_list = []

    for c_area in page.areas:
        for c_paragraph in c_area.paragraphs:
            for c_line in c_paragraph.lines:
                return_list.append(c_line)
                # for c_word in c_line.words:
                    # print(c_word.ocr_text)

    return return_list

def get_abbyy_boxes(filename):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dir_path, filename)
    document = HOCRDocument(full_path, is_path=True)
    # page = document.pages[0]
    return_list = []
    page = document.pages[0]

    html = page._hocr_html
    contents = html.contents
    return_list = []
    for element in contents:
        res = str(element).find("ocr_line")
        if res>=1:
            # in abbyy-hocr sometimes the lines are packed in ocr_careas and sometimes not
            # this reads all the lines in correct order
            if element.attrs['class'][0]=='ocr_carea':
                new_area = Area(None, element)
                for par in new_area.paragraphs:
                    for line in par.lines:
                        return_list.append(line)


            elif element.attrs['class'][0]=='ocr_par':
                par = Paragraph(None,element)
                for line in par.lines:
                    return_list.append(line)

            else:
                raise Exception('THIS SHOULDNT HAPPEN!')



    return return_list

tesslist = get_tesseract_boxes("Testfiles/oneprof_tesseract.html")
abbylist = get_abbyy_boxes("Testfiles/oneprof_abbyy.hocr.html")



def compare_coordinates(coordinates1, coordinates2):
    MODE = "ENDPOINT_TRESHOLD"

    (x1_start, y1_start, x1_end, y1_end) = coordinates1
    (x2_start, y2_start, x2_end, y2_end) = coordinates2

    if MODE == "ENDPOINT_TRESHOLD":
        TRESHOLD_VALUE = 14
        y_start_diff = abs(y1_start - y2_start)
        y_end_diff = abs(y1_end - y2_end)
        if (y_start_diff < TRESHOLD_VALUE and y_end_diff < TRESHOLD_VALUE):
            return True
        else:
            return False
    if MODE == "OVERLAPPING_SIZE":
        TRESHOLD_VALUE = 12


def compare_ocr_strings_cwise(ocr_string1,ocr_string2, ignore_case = False):
    """
    Character-wise comparison of ocr strings
    :param ocr_string1: input string 1
    :param ocr_string2: input string 2
    :param ignore_case: if True, no case sensivity, cast everything (including result) to lowercase
    :return: ocr_string1 subtracted by the characters in ocr_string2
    """

    # simple method for ignore case, just downcast everything to lowercase
    if ignore_case:
        ocr_string1 = ocr_string1.lower()
        ocr_string2 = ocr_string2.lower()

    final_string = ocr_string1
    for char in ocr_string2:
        foundindex = final_string.find(char)
        if foundindex >= 0:
            # final_string_old = final_string.replace(char, ' ') #erroronous replaces all strings
            final_string = final_string.replace(char, ' ', 1)

    return final_string


def compare_ocr_strings_difflib_seqmatch(ocr_string1, ocr_string2):
    """
    difflib sequence matching is based on Ratcliff and Obershelp algorithm
    longest contiguous matching subsequence that contains no “junk” elements

    :param ocr_string1:
    :param ocr_string2:
    :return:
    """
    sqmatch = difflib.SequenceMatcher(None,ocr_string1,ocr_string2,True)

    matching_blocks = sqmatch.get_matching_blocks()
    for idx, block in enumerate(matching_blocks):
        (str1_starti, str2_starti, match_length) = block

        str1_substr = ocr_string1[str1_starti:str1_starti+match_length]
        str2_substr = ocr_string2[str2_starti:str2_starti+match_length]

        print("Block ",str(idx).zfill(4),"str1 match: ",str1_substr)
        print("Block ",str(idx).zfill(4),"str2 match: ",str2_substr)

    # similarity of sequences info
    ratio = sqmatch.ratio()
    print("Similarity ratio is ",ratio)

    # find longest match in a subsequence of strings
    longest_match = sqmatch.find_longest_match(0,10,5,10)

    # operations how to turn ocrstr1 into ocrstr2
    opcodes = sqmatch.get_opcodes()
    opcodes_grouped = sqmatch.get_grouped_opcodes(3)


def compare_ocr_strings_difflib_difftool(ocr_string1, ocr_string2):
    print("compare ocr strings ")
    differ = difflib.Differ(None,None)
    cres = differ.compare(ocr_string1,ocr_string2)
    listres = list(cres)

    print("differ results ")
    for element in listres:
        ctrl_char = element[0:1]
        string = element[1::]
        print("Control char: ",ctrl_char," text: ",string)

    """
        Codes in differ result
        '- ' 	line unique to sequence 1
        '+ ' 	line unique to sequence 2
        '  ' 	line common to both sequences
        '? ' 	line not present in either input sequence
    """


    # Alternative ndiff
    print("ndiff results ")
    ndiff = difflib.ndiff(ocr_string1,ocr_string2)
    ndiflist = list(ndiff)

    for element in ndiflist:
        ctrl_char = element[0:1]
        string = element[1::]
        print("Control char: ", ctrl_char, " text: ", string)


def linify_list(ocr_list):
    """
    Writes all elements which are in one line to the same line to the same list entry
    :param ocr_list:
    :return:
    """
    final_list = []

    for base_line in ocr_list:
        if not hasattr(base_line,'marked'):
            base_line.marked = False
        if not base_line.marked:
            bl_coordinates = base_line.coordinates
            list_for_baseline =[] # each baseline gets a list
            list_for_baseline.append(base_line)
            for comparison_line in ocr_list:
                if base_line is comparison_line:
                    # prevent same lines in array
                    continue

                cl_coordinates = comparison_line.coordinates

                match = compare_coordinates(bl_coordinates,cl_coordinates)
                if match:
                    # line which already has been matched to a cluster can't be baseline anymore
                    comparison_line.marked = True
                    list_for_baseline.append(comparison_line)
            final_list.append(list_for_baseline)

    return final_list


def unify_list_entries(ocr_listlist, mode="OCROPUS"):
    final_list =[]
    for entry in ocr_listlist:
        if len(entry)==1:
            final_list.append(entry[0])
        else:
            text_accu=""
            for line in entry:
                if mode is "OCROPUS":
                    text_accu = text_accu +" "+ line._hocr_html.contents[0]
                else:
                    text_accu = text_accu +" "+ line.ocr_text

            # refactor the first element with accumulated text
            if mode is "OCROPUS":
                entry[0]._hocr_html.contents[0] = text_accu
            else:
                entry[0].ocr_text = text_accu

            final_list.append(entry[0])

    return final_list


def compare_lists(ocro_list, tess_list, abbyy_list):

    Y_TRESH=10
    TESSERACT_COMPARE=False
    ABBY_COMPARE=True

    for ocro_line in ocro_list:
        #search correspondence
        ocro_coordinates = ocro_line.coordinates
        if TESSERACT_COMPARE:
            for tess_line in tess_list:
                tess_coordinates = tess_line.coordinates
                cmpr_result = compare_coordinates(ocro_coordinates,tess_coordinates)
                if cmpr_result:
                    """Extract and subtract text from boxes"""
                    tess_line_text = tess_line.ocr_text
                    print("Tesseract Box:         ", tess_line_text)
                    ocro_line_text = ocro_line._hocr_html.contents[0]
                    print("Ocropus Box  :         ", ocro_line_text)
                    result1 = compare_ocr_strings_cwise(tess_line_text, ocro_line_text)
                    print("tesseract-ocropus:     ", result1)
                    result2 = compare_ocr_strings_cwise(ocro_line_text,tess_line_text)
                    print("ocropus-tesseract:     ", result2)
                    result3 = compare_ocr_strings_cwise(tess_line_text, ocro_line_text, True)
                    print("tesseract-ocropus (ic):", result3)
                    result4 = compare_ocr_strings_cwise(ocro_line_text, tess_line_text, True)
                    print("ocropus-tesseract (ic):", result4)

                    # this just logs blocks



                   # compare_ocr_strings_difflib_seqmatch(ocro_line_text, tess_line_text)


                    result5 = compare_ocr_strings_difflib_difftool(ocro_line_text, tess_line_text)

                    print("--------")
                    break
        if ABBY_COMPARE:
            for abby_line in abbyy_list:
                abbyy_coordinates = abby_line.coordinates
                cmpr_result = compare_coordinates(ocro_coordinates,abbyy_coordinates)
                if cmpr_result:
                    """Extract and subtract text from boxes"""
                    abbyy_line_text = abby_line.ocr_text
                    print("Abbyy Box:         ", abbyy_line_text)
                    ocro_line_text = ocro_line._hocr_html.contents[0]
                    print("Ocropus Box  :         ", ocro_line_text)
                    result1 = compare_ocr_strings_cwise(abbyy_line_text, ocro_line_text)
                    print("abbyy-ocropus:     ", result1)
                    result2 = compare_ocr_strings_cwise(ocro_line_text,abbyy_line_text)
                    print("ocropus-abby:     ", result2)
                    result3 = compare_ocr_strings_cwise(abbyy_line_text, ocro_line_text, True)
                    print("abbyy-ocropus (ic):", result3)
                    result4 = compare_ocr_strings_cwise(ocro_line_text, abbyy_line_text, True)
                    print("ocropus-abbyy (ic):", result4)

                    # this just logs blocks



                   # compare_ocr_strings_difflib_seqmatch(ocro_line_text, tess_line_text)


                   # result5 = compare_ocr_strings_difflib_difftool(ocro_line_text, abbyy_line_text)

                    print("--------")
                    break



ocrolistlist_linified = linify_list(ocrolist)
ocrolist_linified = unify_list_entries(ocrolistlist_linified)

print("NON UNIFIED OCROLIST---------------")
# compare_lists(ocrolist,tesslist)
print("UNIFIED OCROLIST---------------")
print("ocrolist_unified.length: ", len(ocrolist_linified))
print("tesslist.length: ", len(tesslist))
print("abbyylist.length: ", len(abbylist))

compare_lists(ocrolist_linified, tesslist, abbylist)

