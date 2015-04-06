###############################################################################
## oneNN.py
##     1-Nearest Neighbor classifier
##
## Submitted by: Manish Kanadje, Kedarnath Calangutkar
###############################################################################

import numpy
import pdb
import os
import threading
import parser

import normalize as nl
import features as feat
import dataSplit as dsp

from sklearn.externals import joblib
from sklearn import svm
from sklearn import ensemble
from xml.dom import minidom

from random import *
from pylab import *

# Extract training data / or load from pickled files
def getTrainingData(train):
    if train:
        trainData, testData = dsp.updateSplits()
        trainingFeatures = []
        trainingLabels = []

        testFeatures = []
        testLabels = []
        
        print ("Number of training files = " + str(len(trainData)))
        for file in trainData:
            print ("Extracting features for " + file)
            symbolList, labelList = getFileStrokeData(file)
            tempTrainData, tempTrainLabels = feat.featureExtraction(file, symbolList, \
                                                                    labelList)
            trainingFeatures += tempTrainData
            trainingLabels += tempTrainLabels

        print ("Number of test files = " + str(len(testData)))
        for file in testData:
            print ("Extracting features for " + file)
            symbolList, labelList = getFileStrokeData(file)
            tempTestData, tempTestLabels = feat.featureExtraction(file, symbolList, \
                                                                  labelList)
            testFeatures += tempTestData
            testLabels += tempTestLabels
        

        print ("###############################")
        print ("Training 1-Nearest Neighbor Classifier")
        nnClassifier, trainingLabels = createClassifier(trainingFeatures, trainingLabels)
        
        print ("###############################")
        joblib.dump(nnClassifier, '1nnClf.joblib', compress = 3)

        joblib.dump(trainData, 'trainData.joblib', compress = 3)
        joblib.dump(trainingFeatures, 'trainingFeatures.joblib', compress = 3)
        joblib.dump(trainingLabels, 'trainingLabels.joblib', compress = 3)

        joblib.dump(testData, 'testData.joblib', compress = 3)
        joblib.dump(testFeatures, 'testFeatures.joblib', compress = 3)
        joblib.dump(testLabels, 'testLabels.joblib', compress = 3)
    else:
        print ("###############################")
        print ("Loading Pickle Files")
        #nnClassifier = joblib.load('1nnClf.joblib')
        trainData = joblib.load('trainData.joblib')
        trainingFeatures = joblib.load('trainingFeatures.joblib')
        trainingLabels = joblib.load('trainingLabels.joblib')

        testData = joblib.load('testData.joblib')
        testFeatures = joblib.load('testFeatures.joblib')
        testLabels = joblib.load('testLabels.joblib')
        nnClassifier, trainingLabels = createClassifier(trainingFeatures, trainingLabels)
        print ("###############################")
        
    return nnClassifier, trainData, testData, trainingLabels, testLabels

# Perform training and testing on all of the dataset
def statsForData(train):
    nnClassifier, trainData, testData, trainLabels, testLabels = \
       getTrainingData(train)
    print ("###############################")
    print ("Create lg files for training fold")
    
    # Do threading!
    numberOfThreads = 4
    trainDataList = list(trainData.keys())
    length = int(len(trainDataList) / numberOfThreads);
    for i in range(numberOfThreads):
        print("Creating thread for files from " + str(i * length) + " to " + str((i + 1) * length))
        t = threading.Thread(target=performClassification, args = (trainDataList[i * length:(i + 1) * length], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
        t.start()
        
    print("Creating thread for files from " + str(numberOfThreads * length) + " to " + str(trainDataList))
    t = threading.Thread(target=performClassification, args = (trainDataList[numberOfThreads * length:], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
    t.start()
    
    print ("###############################")
    print ("###############################")
    print ("Create lg files for test fold")
    performClassification(testData, nnClassifier, trainLabels, './test_true_lg_NN/', './test_out_lg_NN/')
    print ("###############################")

# Performs classification on a given dataset. (Can be used to generate ground truth files as well)
def performClassification(dataset, trainingFeatures, trainLabels, folderNameTrue, folderNameOut):
    for csv_file in dataset:
        basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
        path = csv_file[:csv_file.rfind('/')]
        path = path[:path.rfind('/') + 1]
        inkml_file = path + basename + '.inkml'
        evaluateFile(trainingFeatures, trainLabels, inkml_file, folderNameOut)
        # parser.convertInkmlToLg(inkml_file, folderNameTrue)

# Extract stroke data from the inkml file
def getFileStrokeData(csv_file):
    basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
    path = csv_file[:csv_file.rfind('/')]
    path = path[:path.rfind('/') + 1]
    inkml_file = path + basename + '.inkml'        
    symbolList, labelList = feat.getStrokeIds(inkml_file)
    return symbolList, labelList 

# returns a numpy matrix form of the training features along with the training labels
def createClassifier(trainingFeatures, trainingLabels):
    mat = numpy.matrix(trainingFeatures)
    return mat, trainingLabels

# Predicts the class of the given feature vector
def predict(trainingFeatures, trainingLabels, featureVector):
    featureMatrix = numpy.matrix(featureVector)
    diff = numpy.subtract(trainingFeatures, featureMatrix)
    squaredDiff = numpy.multiply(diff, diff)
    distance = numpy.sum(squaredDiff, axis=1)
    _class = numpy.argmin(distance)
    return trainingLabels[_class]

# Evaluates all the inkml files in the testFolderPath and stores lg file with same name in folderName
def evaluateData(trainingFeatures, trainLabels, testFolderPath, folderName):
    files = [testFolderPath + f for f in os.listdir(testFolderPath) if os.path.isfile(testFolderPath + f) and f.endswith(".inkml")]

    for inkml_file in files:
        print('Start evaluating :' + inkml_file)
        evaluateFile(trainingFeatures, trainLabels, inkml_file, folderName)

# Evalutes the given inkml file using the provided classifier (i.e. trainingFeatures and trainingLabels) and generates an lg file in folderName
def evaluateFile(trainingFeatures, trainLabels, inkml_file, folderName):
    basename = inkml_file[inkml_file.rfind('/') + 1 : inkml_file.rfind('.')]
    path = inkml_file[:inkml_file.rfind('/') + 1]
    lg_file = folderName + basename + '.lg'
    csv_file = path + 'csv/' + basename + '.csv'
    print ("Evaluating " + inkml_file)

    if not os.path.exists(folderName):
        os.makedirs(folderName)
    
    if not os.path.exists(csv_file):
        parser.convertStrokesToCsv(inkml_file)
    
    symbolList, labelList = feat.getStrokeIdsForTest(inkml_file)

    testFeatures, testLabels = feat.featureExtraction(csv_file, symbolList, labelList)
    results = []

    lg = open(lg_file,'w')

    relations = ""
    inkml_parsed = minidom.parse(inkml_file)
    for i in range(len(testFeatures)):
        result = predict(trainingFeatures, trainLabels, testFeatures[i])
        try:
            symbol_label = findSymbol(inkml_parsed, symbolList[i])
        except:
            pickle.dump(inkml_parsed, open('inkmlp.p', 'wb'))
        if symbol_label == ',':
            symbol_label = 'COMMA'
        result_symbol = 'COMMA' if result == ',' else result
        lg.write("O, " + symbol_label + ", " + result_symbol + ", 1.0")
        for stroke in symbolList[i]:
            lg.write(", " + stroke)
        lg.write("\n")
        if i != len(testFeatures) - 1:
            try:
                next_symbol_label = findSymbol(inkml_parsed, symbolList[i + 1])
            except:
                pickle.dump(inkml_parsed, open('inkmlp.p', 'wb'))
            if next_symbol_label == ',':
                next_symbol_label = 'COMMA'
            relations += "R, " + symbol_label + ", " + next_symbol_label + ", Right, 1.0\n"
    
    lg.write("\n")
    lg.write(relations)
    
    lg.close()

# Returns the label for this symbol from the inkml file
def findSymbol(inkml_parsed, strokeList):
    traceGroups = inkml_parsed.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    for tGroup in traceGroups:
        stroke_id = None
        stroke_found = True 
        strokes = tGroup.getElementsByTagName('traceView')
        for stroke in strokes:
            stroke_id = stroke.attributes["traceDataRef"].nodeValue
            if stroke_id not in strokeList:
                stroke_found = False
                break
        if stroke_found:
            try:
                annotationXML = tGroup.getElementsByTagName('annotationXML')
                symbol = annotationXML[0].attributes["href"].nodeValue
            except:
                symbol = 'AUTO_' + stroke_id
            return symbol.replace(',', 'COMMA')
        
    return None

if __name__ == "__main__":
    statsForData(True)

