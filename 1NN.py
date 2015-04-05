import numpy
from pylab import *
from sklearn import svm
from sklearn import ensemble
from xml.dom import minidom
import pdb
from sklearn.externals import joblib
from random import *
import os
import threading

import normalize as nl
import features as feat
import dataSplit as dsp
import parser

def getTrainingData(UseTrained):
    if UseTrained:
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
        #pdb.set_trace()
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
    #error = 0
    #print ("Total test samples = " + str(len(testFeatures)))
    #for i in range(len(trainingFeatures)):
    #    _class = predict(trainingFeatures, trainingLabels, testFeatures[i])
    #    if i % 100 == 0:
    #        print(str(i) + ": " + _class + " should be " + str(testLabels[i]))
    #    if _class != testLabels[i]:
    #        error += 1
    #print ("Num of samples = " + str(len(testFeatures)))
    #print ("Errors = " + str(error))
    #print ("Rate = " + str((1.0 * error)/len(testFeatures)))
        
    return nnClassifier, trainData, testData, trainingLabels, testLabels

def statsForData():
    nnClassifier, trainData, testData, trainLabels, testLabels = \
       getTrainingData(False)
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for training fold")
    # performClassification(trainData, nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/')
    numberOfSplits = 10
    trainDataList = list(trainData.keys())
    length = int(len(trainDataList) / numberOfSplits);
    for i in range(numberOfSplits):
        t = threading.Thread(target=performClassification, args = (trainDataList[i * length:(i + 1) * length], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
        t.start()
    t = threading.Thread(target=performClassification, args = (trainDataList[numberOfSplits * length:], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
    t.start()
    
    print ("###############################")
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for test fold")
    performClassification(testData, nnClassifier, trainLabels, './test_true_lg_NN/', './test_out_lg_NN/')
    print ("###############################")
    
def statsForDataRemaining():
    pdb.set_trace()
    nnClassifier, trainData, testData, trainLabels, testLabels = getTrainingData(False)
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for training fold")
    # performClassification(trainData, nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/')
    numberOfSplits = 2
    oldTrainDataList = list(trainData.keys())
    #oldTestDataList = list(testData.keys())
    done = [f[:f.rfind('.')] for f in os.listdir('./train_out_lg_NN/') if os.path.isfile('./train_out_lg_NN/' + f) and f.endswith(".lg")]
    trainDataList = [f for f in oldTrainDataList if f[f.rfind('/') + 1:f.rfind('.')] not in done]
    #testDataList = [f for f in oldTestDataList if f[f.rfind('/') + 1:f.rfind('.')] not in done]
    #trainDataList += testDataList
    print(str(trainDataList))
    length = int(len(trainDataList) / numberOfSplits);
    print("Length " + str(length))
    for i in range(numberOfSplits):
        print("From " + str(i * length) + " to " + str((i + 1) * length))
        t = threading.Thread(target=performClassification, args = (trainDataList[i * length:(i + 1) * length], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
        t.start()
        
    print("From " + str(numberOfSplits * length) + " to end")
    t = threading.Thread(target=performClassification, args = (trainDataList[numberOfSplits * length:], nnClassifier, trainLabels, './train_true_lg_NN/', './train_out_lg_NN/'))
    t.start()
    
    print ("###############################")
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for test fold")
    #performClassification(testData, nnClassifier, trainLabels, './test_true_lg_NN/', './test_out_lg_NN/')
    print ("###############################")

def performClassification(dataset, classifier, trainLabels, folderNameTrue, folderNameOut):
    for csv_file in dataset:
        basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
        path = csv_file[:csv_file.rfind('/')]
        path = path[:path.rfind('/') + 1]
        #lg_file = path + 'lg/' + basename + '.lg'        
        inkml_file = path + basename + '.inkml'
        evaluateFile(classifier, trainLabels, inkml_file, folderNameOut)
        parser.convertInkmlToLg(inkml_file, folderNameTrue)

def getFileStrokeData(csv_file):
    basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
    path = csv_file[:csv_file.rfind('/')]
    path = path[:path.rfind('/') + 1]
    #lg_file = path + 'lg/' + basename + '.lg'        
    inkml_file = path + basename + '.inkml'        
    #csv_file = path + 'csv/' + basename + '.csv'    
    symbolList, labelList = feat.getStrokeIds(inkml_file)
    return symbolList, labelList 

def createClassifier(trainingFeatures, trainingLabels):
    mat = numpy.matrix(trainingFeatures)
    return mat, trainingLabels

def predict(trainingFeatures, trainingLabels, featureVector):
    #extendedFeatureMatrix = numpy.matrix([featureVector for i in range(len(trainingLabels))])
    #diff = numpy.subtract(extendedFeatureMatrix, trainingFeatures)
    #pdb.set_trace()
    featureMatrix = numpy.matrix(featureVector)
    diff = numpy.subtract(trainingFeatures, featureMatrix)
    squaredDiff = numpy.multiply(diff, diff)
    distance = numpy.sum(squaredDiff, axis=1)
    _class = numpy.argmin(distance)
    return trainingLabels[_class]
    
def predictOld(trainingFeatures, trainingLabels, featureVector):
    #extendedFeatureMatrix = numpy.matrix([featureVector for i in range(len(trainingLabels))])
    #diff = numpy.subtract(extendedFeatureMatrix, trainingFeatures)
    
    featureMatrix = numpy.matrix(featureVector)
    diff = numpy.subtract(trainingFeatures, featureMatrix)
    squaredDiff = numpy.multiply(diff, diff)
    distance = numpy.sum(squaredDiff, axis=1)
    _class = numpy.argmin(distance)
    return trainingLabels[_class]

def classify1NN(X, Y, f):
    # Find class of nearest neighbor
    least = 99999
    leastClass = -1
    for i in range(len(X)):
        dist = 0
        for n in range(len(X[i])):
            xn = X[i][n]
            dist += (xn - f[n]) ** 2
        if dist < least:
            least = dist
            leastClass = Y[i]
    return leastClass[0]

def classifyAllNN(X, Y, classifier):
    dbX = []
    dbY = []

    # Scan vertically for changes in class
    for x in numpy.arange(minX, maxX, granularity):
        lastoutput = classifier(X, Y, x, minY)
        for y in numpy.arange(minY, maxY, granularity):
            output = classifier(X, Y, x, y)
            if output < 0.5:
                plt.plot(x, y, 'c.')
            elif output >= 0.5:
                plt.plot(x, y, 'y.')
            if (lastoutput < 0.5 and output >= 0.5) or (lastoutput >= 0.5 and output < 0.5):
                dbX.append(x)
                dbY.append(y - granularity/2)
            lastoutput = output

    # Scan horizontally for changes in class
    for y in numpy.arange(minY, maxY, granularity):
        lastoutput = classifier(X, Y, minX, y)
        for x in numpy.arange(minX, maxX, granularity):
            output = classifier(X, Y, x, y)
            if (lastoutput < 0.5 and output >= 0.5) or (lastoutput >= 0.5 and output < 0.5):
                dbX.append(x - granularity/2)
                dbY.append(y)
            lastoutput = output
    plt.plot(dbX, dbY, 'k.')

def evaluateData(rndClassifier, testFolderPath, folderName):
    # testFolderPath = "./TrainINKML_v3/"
    files = [testFolderPath + f for f in os.listdir(testFolderPath) if os.path.isfile(testFolderPath + f) and f.endswith(".inkml")]

    for inkml_file in files:
        print('Start evaluating :', inkml_file)
        evaluateFile(rndClassifier, trainLabels, inkml_file, folderName)
    
        
def evaluateFile(rndClassifier, trainLabels, inkml_file, folderName):
    basename = inkml_file[inkml_file.rfind('/') + 1 : inkml_file.rfind('.')]
    path = inkml_file[:inkml_file.rfind('/') + 1]
    #lg_file = path + 'output_lg/' + basename + '.lg'
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
        result = predict(rndClassifier, trainLabels, testFeatures[i])
        #print (inkml_file)
        #if (inkml_file == './TrainINKML_v3/HAMEX/formulaire003-equation038.inkml'):
        #    pdb.set_trace()
        try:
            symbol_label = findSymbol(inkml_parsed, symbolList[i])
        except:
            pickle.dump(inkml_parsed, open('inkmlp.p', 'wb'))
            pdb.set_trace()
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
                pdb.set_trace()
            if next_symbol_label == ',':
                next_symbol_label = 'COMMA'
            relations += "R, " + symbol_label + ", " + next_symbol_label + ", Right, 1.0\n"
    
    lg.write("\n")
    lg.write(relations)
    
    lg.close()

def findSymbol(inkml_parsed, strokeList):
    traceGroups = inkml_parsed.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    #pdb.set_trace()
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

#statsForData()
statsForDataRemaining()

