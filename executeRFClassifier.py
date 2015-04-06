###############################################################################
## executeRFClassifier.py
##     script to execute the random forest classifier on a
##     specified dataset using pre-trained classifier
##
## Submitted by: Manish Kanadje, Kedarnath Calangutkar
###############################################################################

import sys
import rfClassifier as rf
from sklearn.externals import joblib

# Print usage help
def printUsage():
    print ("Usage:")
    print ("         python executeRFClassifier.py joblib test_folder output_folder")
    print ("")
    print (" joblib          : file_name of stored random forest classifier")
    print (" test_folder     : full path of folder containing inkml files (should end with a '/')")
    print (" output_folder   : full path of folder to output lg files (should end with a '/')")

# main method
def main():
    if len(sys.argv) != 4:
        printUsage()
        sys.exit()
    
    joblib_file_name = sys.argv[1]
    test_inkml_folder_full_path = sys.argv[2]
    output_lg_folder_full_path = sys.argv[3]
    
    classifier = joblib.load(joblib_file_name)
    
    rf.evaluateData(classifier, test_inkml_folder_full_path, output_lg_folder_full_path)

main()
