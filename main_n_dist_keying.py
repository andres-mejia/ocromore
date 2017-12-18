"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from n_dist_keying.hocr_line_normalizer import HocrLineNormalizer
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
from ocr_validation.ocr_validator import OCRvalidator

# Get lists of Hocr-objects from testfiles
hocr_comparator = HocrBBoxComparator()
ocrolist = hocr_comparator.get_ocropus_boxes("../Testfiles/oneprof_ocropus.html")
tesslist = hocr_comparator.get_tesseract_boxes("../Testfiles/oneprof_tesseract.html")
abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy.hocr.html")

# Normalize list results for comparison
hocr_normalizer = HocrLineNormalizer()
ocrolist_normalized = hocr_normalizer.normalize_ocropus_list(ocrolist)


print("List results:---------------")
print("ocrolist_normalized.length: ", len(ocrolist_normalized))
print("tesslist.length: ", len(tesslist))
print("abbyylist.length: ", len(abbylist))

# Show a basic list comparison, with characterwise comparison (depreciated)
# hocr_comparator.compare_lists(ocrolist_normalized, tesslist, abbylist)


# Prepare a basic list object with all ocr's which should be compared
base_ocr_lists = []
base_ocr_lists.append(tesslist)
base_ocr_lists.append(abbylist)
base_ocr_lists.append(ocrolist_normalized)

# Do the actual comparison of ocr lists, this matches lines with the same y-position together and calls them sets
ocr_comparison = hocr_comparator.compare_lists(base_ocr_lists)
ocr_comparison.sort_set()           #sort the created set after the y-height in ocr-documents
ocr_comparison.print_sets(True)     #print the sets created
ocr_comparison.do_n_distance_keying()   #do the keying, which makes the decision which is the best line for each set
ocr_comparison.print_n_distance_keying_results()  #print keying results
ocr_comparison.print_sets(False)    # print the sets again with decision information


ocr_comparison.save_n_distance_keying_results_to_file("./Testfiles/oneprof_keying_result.txt")

# Do steps to validate the used keying
ocr_validator = OCRvalidator()

ignore_linefeed = True
ignore_whitespace = True
"""
ocr_validator.set_groundtruth("./Testfiles/oneprof.gt.txt")
ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_tesseract_questionmark.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace, True)
"""
ocr_validator.set_groundtruth("./Testfiles/oneprof.gt.txt")
ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_tesseract_questionmark.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)

# todo implement proper error rating against ground-truth
# todo implement difference matching