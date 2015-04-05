from sklearn.externals import joblib

import oneNN as nn
import sys

def printUsage():
    print ("Usage:")
    print ("         executeNNClassifier.py training_features_joblib training_labels_joblib test_folder output_folder")
    print ("")
    print (" training_features_joblib  : file_name of stored 1-nearest neighbor classifier")
    print (" training_labels_joblib    : file_name of stored 1-nearest neighbor classifier")
    print (" test_folder               : full path of folder containing inkml files (should end with a '/')")
    print (" output_folder             : full path of folder to output lg files (should end with a '/')")

def main():
    if len(sys.argv) != 5:
        printUsage()
        sys.exit()
    
    training_features_joblib_file_name = sys.argv[1]
    training_labels_joblib_file_name = sys.argv[2]
    test_inkml_folder_full_path = sys.argv[3]
    output_lg_folder_full_path = sys.argv[4]
    
    training_features = joblib.load(training_features_joblib_file_name)
    training_labels = joblib.load(training_labels_joblib_file_name)
    
    nnClassifier, training_labels = nn.createClassifier(training_features, training_labels)
    
    nn.evaluateData(nnClassifier, training_labels, test_inkml_folder_full_path, output_lg_folder_full_path)

main()
