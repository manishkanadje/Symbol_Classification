import numpy
#from pylab import *
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
        tempTrainData, tempTrainLabels = feat.featureExtraction(file)
        trainingFeatures += tempTrainData
        trainingLabels += tempTrainLabels

    for file in testData:
        #testFeatures, testLabels = feat.featureExtraction(file)
        tempTestData, tempTestLabels = feat.featureExtraction(file)
        testFeatures += tempTestData
        testLabels += tempTestLabels
    pdb.set_trace()
    
    #print (len(featureList))
    for i in range(len(testFeatures)):
        results = classify1NN(trainingFeatures, trainingLabels, testFeatures[i], testLabels[i])
        count  = 0
        for i in range(len(results)):
            if (results[i] == testLabels[i]):
                count += 1
        print (count/len(testLabels))
    pdb.set_trace()
    print ("Done Training")

def plotXY(X, Y):
    errors = 0
    c = [[0, 0], [0, 0]]
    for i in range(len(X)):
        output = classify1NN(X, Y, X[i][1], X[i][2])
        if Y[i][0] == 0:
            plt.plot(X[i][1], X[i][2], 'bs')
            if output < 0.5:
                c[0][0] += 1
            else:
                c[0][1] += 1
        elif Y[i][0] == 1:
            plt.plot(X[i][1], X[i][2], 'y*')
            if output < 0.5:
                c[1][0] += 1
            else:
                c[1][1] += 1
        else:
            print("ERROR: Unexpected target value!")
    errors = c[0][1] + c[1][0]
    total = len(X)
    percent = (total - errors)/total * 100
    print("Classification Rate = %.2f %%" % percent)
    print("Confusion matrix:")
    print("                 " + "  Alg. Output")
    print("                 " + "    0     1")
    print(" Ground Truth/ 0 " + "   " + str(c[0][0]) + "    " + str(c[0][1]))
    print("    Target     1 " + "   " + str(c[1][0]) + "    " + str(c[1][1]))
    

def classify1NN(X, Y, f):
    # Find class of nearest neighbor
    least = 99999
    leastClass = -1
    for i in range(len(X)):
        dist = 0
        for n in range(len(X[i])):
            xn = X[i][n]
            dist += (x1 - f[n]) ** 2
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

getTrainingData()
