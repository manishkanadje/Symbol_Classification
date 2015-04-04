from pylab import *
from sklearn import svm
from sklearn import ensemble
import pdb
from random import *

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
    rndClassifier = ensemble.RandomForestClassifier(n_estimators = 2000, max_depth = 10)
    
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
        
    
getTrainingData()

