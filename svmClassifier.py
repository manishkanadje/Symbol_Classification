from pylab import *
from sklearn import svm
from sklearn import ensemble
import pdb
from random import *

import normalize as nl
import features as feat

def getTrainingData():
    featureList, labelList = feat.fileCall()
    #pdb.set_trace()
    #svmClassifier = svm.SVC()
    rndClassifier = ensemble.RandomForestClassifier(n_estimators = 500)
    print len(featureList)
    trainData, trainLabels, testData, testLabels = splitData(featureList, labelList)
    #svmClassifier.fit(trainData, trainLabels)
    print len(trainData)
    print len(testData)
    rndClassifier.fit(trainData, trainLabels)
    #results = svmClassifier.predict(testData)
    results = rndClassifier.predict(testData)
    count  = 0
    for i in range(len(results)):
        if (results[i] == testLabels[i]):
            count += 1
    print (count/len(testLabels))
    pdb.set_trace()
    print ("Done Training")

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

