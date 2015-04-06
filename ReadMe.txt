To test the 1-Nearest Neighbor classifier (trained on all of the dataset) against a folder containing inkml files:
    Step 1: extract the tarball using: tar -xzf clf.tar.gz
    Step 2: execute: python executeNNClassifier.py ./testJoblib/all_rndClf.joblib <inkml_folder> <lg_output_folder>

To test the Random Forest classifier (trained on all of the dataset) against a folder containing inkml files:
    Step 1: extract the tarball using: tar -xzf clf.tar.gz
    Step 2: execute: python executeRFClassifier.py ./testJoblib/all_rndClf.joblib <inkml_folder> <lg_output_folder>


The following scenarios assume that the directory structure of the dataset is as provided in mycourses (i.e. ./TrainINKML_v3/expressmatch/*.inmkl, ./TrainINKML_v3/HAMEX/*.inkml, etc) 
To train the classifier using test it (using 2/3 - 1/3 split) for 1-Nearest Neighbor: 
    Step 1: execute: python oneNN.py

To train the classifier using test it (using 2/3 - 1/3 split) for Random Forest: 
    Step 1: execute: python rfClassifier.py

