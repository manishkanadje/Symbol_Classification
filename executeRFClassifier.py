from sklearn.externals import joblib

import rfClassifier as rf
import sys

def printUsage():
    print ("Usage:")
    print ("         executeRFClassifier.py joblib test_folder output_folder")
    print ("")
    print (" joblib          : file_name of stored random forest classifier")
    print (" test_folder     : full path of folder containing inkml files (should end with a '/')")
    print (" output_folder   : full path of folder to output lg files (should end with a '/')")

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
