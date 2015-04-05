import os

trainingFolderPath = "/home/kedarnath/Desktop/NN_output/train_out_lg_NN/"
testingFolderPath = "/home/kedarnath/Desktop/NN_output/test_out_lg_NN/"

trainFiles = [f for f in os.listdir(trainingFolderPath) if os.path.isfile(trainingFolderPath + f) and f.endswith(".lg")]
testFiles = [f for f in os.listdir(testingFolderPath) if os.path.isfile(testingFolderPath + f) and f.endswith(".lg")]

print("Checking all files...")
for f in testFiles:
    if f in trainFiles:
        print ("File " + f + " is in both datasets")

