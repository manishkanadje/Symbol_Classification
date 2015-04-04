from pylab import *
from sklearn import svm
from sklearn import ensemble
from sklearn.externals import joblib
from xml.dom import minidom
import pdb
import os
import pickle
from random import *
from sklearn import metrics
import pickle

import normalize as nl
import features as feat
import dataSplit as dsp

def getTrainingData():
    trainData, testData = dsp.updateSplits()
    trainingFeatures = []
    trainingLabels = []

    testFeatures = []
    testLabels = []
    #featureList, labelList = feat.fileCall()
    #pdb.set_trace()
    #svmClassifier = svm.SVC()
    for file in trainData:
        #pdb.set_trace()
        #trainingFeatures, trainingLabels = feat.featureExtraction(file)
        symbolList, labelList = getFileStrokeData(file)
        tempTrainData, tempTrainLabels = feat.featureExtraction(file, symbolList, \
                                                                labelList)
        trainingFeatures += tempTrainData
        trainingLabels += tempTrainLabels

    for file in testData:
        #testFeatures, testLabels = feat.featureExtraction(file)
        symbolList, labelList = getFileStrokeData(file)
        tempTestData, tempTestLabels = feat.featureExtraction(file, symbolList, \
                                                              labelList)
        testFeatures += tempTestData
        testLabels += tempTestLabels
    #pdb.set_trace()
    rndClassifier = ensemble.RandomForestClassifier(n_estimators = 500, max_depth = 15)
    
    #print (len(featureList))
    #trainData, trainLabels, testData, testLabels = splitData(featureList, labelList)
    #svmClassifier.fit(trainData, trainLabels)
    #print len(trainData)
    #print len(testData)
    print ("###############################")
    print ("Training Random Forest Classifier")
    rndClassifier.fit(trainingFeatures, trainingLabels)
    print ("Training completed")
    print ("###############################")
    #results = svmClassifier.predict(testData)
    results = rndClassifier.predict(testFeatures)
    count  = 0
    for i in range(len(results)):
        if (results[i] == testLabels[i]):
            count += 1
    print (count/len(testLabels))
    pdb.set_trace()
    print ("Done Training")
    return rndClassifier


def getFileStrokeData(csv_file):
    basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
    path = csv_file[:csv_file.rfind('/')]
    path = path[:path.rfind('/') + 1]
    #lg_file = path + 'lg/' + basename + '.lg'        
    inkml_file = path + basename + '.inkml'        
    #csv_file = path + 'csv/' + basename + '.csv'    
    symbolList, labelList = feat.getStrokeIds(inkml_file)
    return symbolList, labelList 
    
def splitData(features, labels):
    testData = []
    testLabels = []
    testSize = int(len(features) * 0.3)
    trainSize = len(features) - testSize
    for i in range(testSize):
        index = randrange(0, len(features))
        testData.append(features.pop(index))
        testLabels.append(labels.pop(index))
    return features, labels, testData, testLabels
        
def evaluateData(rndClassifier, testFolderPath):
    # testFolderPath = "./TrainINKML_v3/"
    testData = []
    testFeatures = []
    testLabels = []

    files = [testFolderPath + f for f in os.listdir(testFolderPath) if os.path.isfile(testFolderPath + f) and f.endswith(".inkml")]


    if not os.path.exists('./output_lg/'):
        os.makedirs('./output_lg/')

    for inkml_file in files:
        print('Start evaluating :', inkml_file)
        evaluateFile(rndClassifier, inkml_file)
        
def evaluateFile(rndClassifier, inkml_file):
    basename = inkml_file[inkml_file.rfind('/') + 1 : inkml_file.rfind('.')]
    path = inkml_file[:inkml_file.rfind('/') + 1]
    #lg_file = path + 'output_lg/' + basename + '.lg'
    lg_file = './output_lg/' + basename + '.lg'
    csv_file = path + 'csv/' + basename + '.csv'
    
    if not os.path.exists(csv_file):
        parser.convertStrokesToCsv(inkml_file)
    
    symbolList, labelList = feat.getStrokeIdsForTest(inkml_file)

    testFeatures, testLabels = feat.featureExtraction(csv_file, symbolList, labelList)
    results = rndClassifier.predict(testFeatures)

    lg = open(lg_file,'w')

    relations = ""
    inkml_parsed = minidom.parse(inkml_file)
    for i in range(len(results)):
        symbol_label = findSymbol(inkml_parsed, symbolList[i])
        lg.write("O, " + symbol_label + ", " + results[i] + ", 1.0")
        for stroke in symbolList[i]:
            lg.write(", " + stroke)
        lg.write("\n")
        if i != len(results) - 1:
            next_symbol_label = findSymbol(inkml_parsed, symbolList[i + 1])
            relations += "R, " + symbol_label + ", " + next_symbol_label + ", Right, 1.0\n"
    
    lg.write("\n")
    lg.write(relations)
    
    lg.close()

def findSymbol(inkml_parsed, strokeList):
    traceGroups = inkml_parsed.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    
    for tGroup in traceGroups:
        stroke_found = True 
        strokes = tGroup.getElementsByTagName('traceView')
        for stroke in strokes:
            stroke_id = stroke.attributes["traceDataRef"].nodeValue
            if stroke_id not in strokeList:
                stroke_found = False
                break
        if stroke_found:
            annotationXML = tGroup.getElementsByTagName('annotationXML')
            return annotationXML[0].attributes["href"].nodeValue
        
    return None


rndClassifier = getTrainingData()
evaluateData(rndClassifier, "./TrainINKML_v3/extension/")

