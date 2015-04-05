#from pylab import *
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
import parser

import normalize as nl
import features as feat
import dataSplit as dsp

def getTrainingData(trainFlag):
    if (trainFlag):
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
            tempTrainData, tempTrainLabels = feat.featureExtraction(file, \
                                                    symbolList,labelList)
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
        rndClassifier = ensemble.RandomForestClassifier(n_estimators = 10, max_depth = 1)

        print ("###############################")
        print ("Training Random Forest Classifier")
        rndClassifier.fit(trainingFeatures, trainingLabels)
        print ("Training completed")
        print ("###############################")
        #pdb.set_trace()
        joblib.dump(rndClassifier, 'rndClf.joblib', compress = 3)

        joblib.dump(trainData, 'trainData.joblib', compress = 3)
        joblib.dump(trainingFeatures, 'trainingFeatures.joblib', compress = 3)
        joblib.dump(trainingLabels, 'trainingLabels.joblib', compress = 3)

        joblib.dump(testData, 'testData.joblib', compress = 3)
        joblib.dump(testFeatures, 'testFeatures.joblib', compress = 3)
        joblib.dump(testLabels, 'testLabels.joblib', compress = 3)
    else:
        print ("###############################")
        print ("Loading Pickle Files")
        rndClassifier = joblib.load('rndClf.joblib')
        trainData = joblib.load('trainData.joblib')
        trainingFeatures = joblib.load('trainingFeatures.joblib')
        trainingLabels = joblib.load('trainingLabels.joblib')

        testData = joblib.load('testData.joblib')
        testFeatures = joblib.load('testFeatures.joblib')
        testLabels = joblib.load('testLabels.joblib')
        print ("###############################")
    #print (len(featureList))
    #trainData, trainLabels, testData, testLabels = splitData(featureList, labelList)
    #svmClassifier.fit(trainData, trainLabels)
    #print len(trainData)
    #print len(testData)
    print ("###############################")
    print ("Classification rate for train data on symbol basis:")
    results = rndClassifier.predict(trainingFeatures)
    count  = 0
    for i in range(len(results)):
        if (results[i] == trainingLabels[i]):
            count += 1
    print (count/len(trainingLabels))
    print ("###############################")
    
    print ("###############################")
    print ("Classification rate for test data on symbol basis:")
    results = rndClassifier.predict(testFeatures)
    count  = 0
    for i in range(len(results)):
        if (results[i] == testLabels[i]):
            count += 1
    print (count/len(testLabels))
    print ("###############################")
    #pdb.set_trace()
    #print ("Done Training")
    return rndClassifier, trainData, testData, trainingLabels, testLabels

def performClassification(dataset, classifier, folderNameTrue, folderNameOut):
    for csv_file in dataset:
        basename = csv_file[csv_file.rfind('/') + 1:csv_file.rfind('.')]
        path = csv_file[:csv_file.rfind('/')]
        path = path[:path.rfind('/') + 1]
        #lg_file = path + 'lg/' + basename + '.lg'        
        inkml_file = path + basename + '.inkml'
        evaluateFile(classifier, inkml_file, folderNameOut)
        parser.convertInkmlToLg(inkml_file, folderNameTrue)
        
def statsForData():
    rndClassifier, trainData, testData, trainLabels, testLabels = \
       getTrainingData(True)
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for training fold")
    performClassification(trainData, rndClassifier, './train_true_lg/', './train_out_lg/')
    print ("###############################")
    #pdb.set_trace()
    print ("###############################")
    print ("Create lg files for test fold")
    performClassification(testData, rndClassifier, './test_true_lg/', './test_out_lg/')
    print ("###############################")

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
        
def evaluateData(rndClassifier, testFolderPath, folderName):
    # testFolderPath = "./TrainINKML_v3/"
    files = [testFolderPath + f for f in os.listdir(testFolderPath) if os.path.isfile(testFolderPath + f) and f.endswith(".inkml")]

    for inkml_file in files:
        print('Start evaluating :', inkml_file)
        evaluateFile(rndClassifier, inkml_file, folderName)
    
        
def evaluateFile(rndClassifier, inkml_file, folderName):
    basename = inkml_file[inkml_file.rfind('/') + 1 : inkml_file.rfind('.')]
    path = inkml_file[:inkml_file.rfind('/') + 1]
    #lg_file = path + 'output_lg/' + basename + '.lg'
    lg_file = folderName + basename + '.lg'
    csv_file = path + 'csv/' + basename + '.csv'

    if not os.path.exists(folderName):
        os.makedirs(folderName)
    
    if not os.path.exists(csv_file):
        parser.convertStrokesToCsv(inkml_file)
    
    symbolList, labelList = feat.getStrokeIdsForTest(inkml_file)

    testFeatures, testLabels = feat.featureExtraction(csv_file, symbolList, labelList)
    results = rndClassifier.predict(testFeatures)

    lg = open(lg_file,'w')

    relations = ""
    inkml_parsed = minidom.parse(inkml_file)
    for i in range(len(results)):
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
        result_symbol = 'COMMA' if results[i] == ',' else results[i]
        lg.write("O, " + symbol_label + ", " + result_symbol + ", 1.0")
        for stroke in symbolList[i]:
            lg.write(", " + stroke)
        lg.write("\n")
        if i != len(results) - 1:
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



#rndClassifier = getTrainingData()
#evaluateData(rndClassifier, "./TrainINKML_v3/extension/", "./out_lg/")
statsForData()
