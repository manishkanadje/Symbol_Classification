import numpy
from pylab import *
from sklearn import svm
from sklearn import ensemble
import pdb
from sklearn.externals import joblib
from random import *

import normalize as nl
import features as feat
import dataSplit as dsp

def getTrainingData(UseTrained):
    if UseTrained:
        trainData, testData = dsp.updateSplits()
        trainingFeatures = []
        trainingLabels = []

        testFeatures = []
        testLabels = []
        
        print ("Number of training files = " + str(len(trainData)))
        for i in range(len(trainData)):
        
            print ("Extracting features for " + trainData[i])
            symbolList, labelList = getFileStrokeData(trainData[i])
            tempTrainData, tempTrainLabels = feat.featureExtraction(trainData[i], symbolList, \
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
        nnClassifier = createClassifier(trainingFeatures, trainingLabels)
        
        joblib.dump(trainingFeatures, 'trainingFeatures.joblib', compress=3)
        joblib.dump(trainingLabels, 'trainingLabels.joblib',compress=3)
    else:
        trainingFeatures = joblib.load('trainingFeatures.joblib')
        trainingLabels = joblib.load('trainingLabels.joblib')
    print ("Training completed")
    print ("###############################")
    print ("Done Training")
    error = 0
    print ("Total test samples = " + str(len(trainingFeatures)))
    for i in range(len(trainingFeatures)):
        _class = predict(trainingFeatures, trainingLabels, trainingFeatures[i])
        #if i % 100 == 0:
        print(str(i) + ": " + _class + " should be " + str(trainingLabels[i]))
        if _class != trainingLabels[i]:
            error += 1
    print ("Num of samples = " + str(len(trainingFeatures)))
    print ("Errors = " + str(error))
    print ("Rate = " + str((1.0 * error)/len(trainingFeatures)))
        
    return nnClassifier, trainData, testData, trainingLabels, testLabels

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

getTrainingData(False)
