"""
   This is a starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying the
   other one is multi sequence alignment best of.

   This file has hardcoded options and path and is rather
   to test functionalities and display results. It doesn't
   work as the main_combine_data step with the main_prepare_dataset
   approach, but has it's own preparation methods.

   Pycharm is recommended here, especially if showing results
"""

from n_dist_keying.hocr_line_normalizer import HocrLineNormalizer
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
from n_dist_keying.hocr_line_height import LineHeightCalculator
from n_dist_keying.textfile_generator import TextFileGenerator
from ocr_validation.ocr_validator import OCRvalidator
from ocr_validation.visualization_handler import VisualizationHandler


# line height adaption settings:
EXPORT_ADAPTED_ABBYY_RESULT = True      # export line height adapted result abbyy
EXPORT_ADAPTED_OCROPUS_RESULT = True    # export line height adapted result ocropus

# un-/refspacing settings:
USE_REFSPACING = False  # instead of unspacing algorithm use the refspacing algorithm

# keying mechanism
DO_N_DIST_KEYING = True                 # do a best of keying by comparing edit distance
DO_MSA_BEST = True                      # do a characterwise best of keying method with preceding alignment

# Settings for Multi Sequence Alignment Best
MSA_BEST_USE_N_DIST_PIVOT = True        # use the best result of N_DIST_KEYING as a pivot 'middle element' in multi-sequence alignment

# postcorrection settings:
KEYING_RESULT_POSTCORRECTION = True     # do postcorrection filters after keying

# validation settings:
IGNORE_LINEFEED = False                 # don't count linefeed for validation comparisons
IGNORE_WHITESPACE = False               # don't count in whitespae for validation comparisons
DISPLAY_DIFFERENCES = False             # activate to show file differences to groundtruth and so on
DO_ISRI_VAL = True                      # validate results with isri tools

# FILENAMES:
FILEPATH_ABBYY_TEXT = "./Testfiles/oneprof_abbyy_result_lh_adapted.txt"
FILEPATH_OCROPUS_TEXT = "./Testfiles/oneprof_ocropus_result_lh_adapted.txt"
FILEPATH_TESSERACT_TEXT = "./Testfiles/oneprof_tesseract_sure.txt"
FILEPATH_GROUNDTRUTH = "./Testfiles/oneprof.gt.txt"



FILEPATH_MSA_BEST_RESULT = "./Testfiles/oneprof_msa_best_result.txt"


# Get lists of Hocr-objects from testfiles (returns lists of hocr-line-objects)
hocr_comparator = HocrBBoxComparator()
ocrolist = hocr_comparator.get_ocropus_boxes("../Testfiles/oneprof_ocropus.html")
tesslist = hocr_comparator.get_tesseract_boxes("../Testfiles/oneprof_tesseract_sure.html")
# abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy.hocr.html") #original abbyy tables
abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy_tables_ok.hocr.html")

#todo: Possibility calculate linefeed with additional information in unnormalized boxes

# Normalize list results for comparison (adapt content to make comparable)
hocr_normalizer = HocrLineNormalizer()
ocrolist_normalized = hocr_normalizer.normalize_ocropus_list(ocrolist)
abbylist_normalized = hocr_normalizer.normalize_abbyy_list(abbylist)
tesslist_normalized = hocr_normalizer.normalize_tesseract_list(tesslist)

print("List results:---------------")
print("ocrolist_normalized.length: ", len(ocrolist_normalized))
print("tesslist.length: ", len(tesslist_normalized))
print("abbyylist.length: ", len(abbylist_normalized))

# Calculate line height in files, used for making linebreaks in merged ocr-output # todo get for pages
lh_calculator = LineHeightCalculator()

lhi_abbyy_normalized = lh_calculator.calculate_line_distance_information(abbylist_normalized, False, True, "abbyy_normalized")
lhi_tesseract_normalized = lh_calculator.calculate_line_distance_information(tesslist_normalized, False, True, "tesseract_normalized")
lhi_ocropus_normalized = lh_calculator.calculate_line_distance_information(ocrolist_normalized, False, True, "ocropus_normalized")


# Show a basic list comparison, with characterwise comparison (depreciated)
# hocr_comparator.compare_lists(ocrolist_normalized, tesslist, abbylist)
# exit(0)



if EXPORT_ADAPTED_ABBYY_RESULT:
    """
        Abbyy output comes only in html-hocr. Therefore the output has to be adapted.
        Some hocr-tools are used to create text https://github.com/tmbdev/hocr-tools
        (please check which exactly). They don't put in line feeds in text. So this
        utilizes the comparator to add some linefeeds (report this to converter-maintainers 
        if necessary)
    """
    tfg = TextFileGenerator()
    tfg.create_file(lhi_abbyy_normalized, abbylist_normalized, FILEPATH_ABBYY_TEXT)


if EXPORT_ADAPTED_OCROPUS_RESULT:
    # if activated ocropus adapted textfile gets exported to set filepath
    tfg2 = TextFileGenerator()
    tfg2.create_file(lhi_ocropus_normalized, ocrolist_normalized, FILEPATH_OCROPUS_TEXT)



# Prepare a basic list object with all ocr's which should be compared
base_ocr_lists = []
base_ocr_lists.append(abbylist_normalized)
base_ocr_lists.append(tesslist_normalized)
base_ocr_lists.append(ocrolist_normalized)

# Do the actual comparison of ocr lists, this matches lines with the same y-position together and calls them sets
ocr_comparison = hocr_comparator.compare_lists(base_ocr_lists)
# add line information in the order the base ocr lists where appended
ocr_comparison.add_line_information(lhi_abbyy_normalized)
ocr_comparison.add_line_information(lhi_tesseract_normalized)
ocr_comparison.add_line_information(lhi_ocropus_normalized)
# sort the created set after the y-height in ocr-documents
ocr_comparison.sort_set()
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)

# use reference spacing to adapt spacing characteristics in 3 files ( for example if the writing is locked)
if USE_REFSPACING:
    ocr_comparison.refspace_list(2, 1)  # refspace ocropus with tesseract as unspacing template
    #ocr_comparison.refspace_list(0, 1)  # refspace abbyy with tesseract as unspacing template, seems to produce worse keying-results

else:
    ocr_comparison.unspace_list(2, 1)  # unspace ocropus with tesseract as unspacing template
    # ocr_comparison.unspace_list(0, 1)  # unspace abbyy with tesseract as unspacing template

print("Print mean||decision||abbyy||tesseract||ocropus|||| ocropus and abbyy un- or refspaced--------------------")
ocr_comparison.print_sets(False)



ocr_comparison.print_sets(True)     # print the sets created

if DO_N_DIST_KEYING:
    # do the actual n-distance keying (best of decision by edit distance)
    ocr_comparison.do_n_distance_keying()               # do the keying, which makes the decision which is the best line for each set
    ocr_comparison.print_n_distance_keying_results()    # print keying results

    if KEYING_RESULT_POSTCORRECTION:
        # do postcorrection steps if active
        ocr_comparison.do_postcorrection(True)
        print("keying results after postcorrection")
        ocr_comparison.print_n_distance_keying_results()

    # save results
    ocr_comparison.save_n_distance_keying_results_to_file("./Testfiles/oneprof_keying_result.txt", True)

if DO_MSA_BEST:
    # do msa-best with pivot and save results
    if MSA_BEST_USE_N_DIST_PIVOT:
        ocr_comparison.do_msa_best_with_ndist_pivot()
    else:
        ocr_comparison.do_msa_best()
    # print results to log and save dataset
    ocr_comparison.print_msa_best_results()
    ocr_comparison.save_dataset_to_file(FILEPATH_MSA_BEST_RESULT, 0, True, "msa_best")

ocr_comparison.print_sets(False)    # print the sets again with decision information

DO_OWN_VAL = False
if DO_OWN_VAL is True:
    # use a custom implemented edit distance based form of validation

    # Do steps to validate the used keying
    ocr_validator = OCRvalidator()

    ocr_validator.set_groundtruth(FILEPATH_GROUNDTRUTH)
    ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
    ocr_validator.set_ocr_file(FILEPATH_MSA_BEST_RESULT)
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
    ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
    ocr_validator.set_ocr_file(FILEPATH_ABBYY_TEXT)
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
    ocr_validator.set_ocr_file(FILEPATH_TESSERACT_TEXT)
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
    ocr_validator.set_ocr_file(FILEPATH_OCROPUS_TEXT)
    ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)


if DO_ISRI_VAL is True:
    from ocr_validation.isri_handler import IsriHandler
    # do a isri-tools based validation and output results

    isri_handler = IsriHandler()
    FILEPATH_ACCURACY_REPORT_MSA = "./Testfiles/isri_accreport_msa_best.txt"
    FILEPATH_ACCURACY_REPORT_NDIST = "./Testfiles/isri_accreport_ndist_keying.txt"

    FILEPATH_ACCURACY_REPORT_ABBYY = "./Testfiles/isri_accreport_abbyy.txt"
    FILEPATH_ACCURACY_REPORT_TESS = "./Testfiles/isri_accreport_tesseract.txt"
    FILEPATH_ACCURACY_REPORT_OCRO = "./Testfiles/isri_accreport_ocro.txt"


    FILEPATH_SYNCTEXT_REPORT_MSA = "./Testfiles/isri_accreport_msa_best_synctest.txt"

    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, "./Testfiles/oneprof_keying_result.txt",FILEPATH_ACCURACY_REPORT_NDIST)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, FILEPATH_ACCURACY_REPORT_MSA)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT, FILEPATH_ACCURACY_REPORT_ABBYY)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_OCROPUS_TEXT, FILEPATH_ACCURACY_REPORT_OCRO)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_TESSERACT_TEXT, FILEPATH_ACCURACY_REPORT_TESS)

    synctext_config = isri_handler.SynctextConfig()
    synctext_config.use_H_algorithm()
    synctext_config.use_T_algorithm()
    isri_handler.synctext([FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT], path_generatedfile=FILEPATH_SYNCTEXT_REPORT_MSA, synctext_config = synctext_config)

# show differences (change invoces to meld if not in pycharm)
if DISPLAY_DIFFERENCES:
    pyc_handler = VisualizationHandler()
    pyc_handler.show_file_comparison_pycharm(FILEPATH_GROUNDTRUTH, "./Testfiles/oneprof_keying_result.txt")
    # mind this is the line height adapted text, generated by this file
    pyc_handler.show_file_comparison_pycharm(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT)
    pyc_handler.show_file_comparison_pycharm(FILEPATH_GROUNDTRUTH, FILEPATH_OCROPUS_TEXT)
    pyc_handler.show_file_comparison_pycharm(FILEPATH_GROUNDTRUTH, FILEPATH_TESSERACT_TEXT)
    pyc_handler.show_file_comparison_pycharm(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT)

