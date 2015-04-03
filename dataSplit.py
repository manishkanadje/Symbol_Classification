from pylab import *
import normalize as nl
from random import *
import pdb
import scipy.stats
import os
import parser
import fnmatch
import features as feat
import copy

dataPriorList = []
RANDOM_SWAPS = 100

def readAllInputData():
    # Final Data Structures
    fileLabelsData = {}
    labelPriors = {}
    labelCount = 0
    
    trainingFolderPath = "./TrainINKML_v3/"
    trainingPaths = [trainingFolderPath + f + "/" for f in os.listdir(trainingFolderPath) if os.path.isdir(trainingFolderPath + f)]
    # For a specific folder
    # trainingPaths = [trainingFolderPath + "MfrDB/"]
    
    #for i in range(len(trainingPaths)):
    for i in range(1):
        path = trainingPaths[i]
        files = [path + f for f in os.listdir(path) if os.path.isfile(path + f) and f.endswith(".inkml")]
        # for a specific file in that folder
        # files = [path + 'MfrDB0033.inkml']
        for inkml_file in files:
            print('Start processing :', inkml_file)
                
            basename = inkml_file[inkml_file.rfind('/') + 1:inkml_file.rfind('.')]
            path = inkml_file[:inkml_file.rfind('/') + 1]
            lg_file = path + 'lg/' + basename + '.lg'        
            csv_file = path + 'csv/' + basename + '.csv'
            
            if not os.path.exists(csv_file):
                parser.convertStrokesToCsv(inkml_file)
            if not os.path.exists(lg_file):
                parser.convertInkmlToLg(inkml_file)

            # Dictionary which contains the list of symbols which are present
            # in csv_files
            symbolList, labelList = feat.getStrokeIds(lg_file)
            fileLabelsData[csv_file] = labelList
            for label in labelList:
                if label not in labelPriors:
                    labelPriors[label] = 1
                else:
                    labelPriors[label] += 1
            labelCount += 1
            
        #pdb.set_trace()
    return labelPriors, fileLabelsData, labelCount

# Create training and test splits based on distribution
def createSplits():
    global dataPriorList
    labelPriors, fileLabelData, labelCount = readAllInputData()
    trainSize = int(len(fileLabelData) * 0.66)
    testSize = len(fileLabelData) - trainSize
    fileNameList = list(fileLabelData.keys())
    for label in labelPriors:
        dataPriorList.append(labelPriors[label]/float(labelCount))
    testData = {}
    testPriors = {}
    testCount = 0
    for i in range(testSize):
        randomIndex = randrange(0, len(fileLabelData))
        fileName = fileNameList[i]
        labelList = fileLabelData[fileName]
        testData[fileName] = labelList
        for label in labelList:
            if label not in testPriors:
                testPriors[label] = 1
            else:
                testPriors[label] += 1
            labelPriors[label] -= 1
            testCount += 1
        fileLabelData.pop(fileName, labelList)
    return fileLabelData, labelPriors, labelCount - testCount, testData, \
        testPriors, testCount

def updateSplits():
    global dataPriorList, RANDOM_SWAPS
    trainData, trainPriors, trainCount, testData, testPriors, testCount = \
      createSplits()

    print ("###############################")
    print ("Datasets Created")
    print ("###############################")
    trainPriorList = []
    trainLabelList = []
    testPriorList = []
    testLabelList = []
    trainCountList = []
    testCountList = []
    for label in trainPriors:
        trainLabelList.append(label)
        testLabelList.append(label)
        trainCountList.append(trainPriors[label])
        testCountList.append(testPriors[label])
        trainPriorList.append(trainPriors[label]/float(trainCount))
        testPriorList.append(testPriors[label]/float(testCount))
    #pdb.set_trace()
    print ("###############################")
    print ("Initial KL Divergence")
    divergenceKL = scipy.stats.entropy(trainPriorList, dataPriorList)
    print ("###############################")
    pdb.set_trace()
    for i in range(RANDOM_SWAPS):
        swapTrainElements, swapTrainList, swapTestElements, swapTestList = \
            swapDistributions(trainData, \
            trainLabelList, trainCountList, trainPriorList, trainCount,
             testData, testLabelList, testCountList, testPriorList, testCount)
        print ("###############################")
        print ("KL Divergence for after swap", i + 1)
        updateDKL = scipy.stats.entropy(swapTrainList, dataPriorList)
        print (updateDKL)
        print ("###############################")
        if (updateDKL < divergenceKL):
            swapDataFromDict(trainData, testData, swapTrainElements)
            swapDataFromDict(testData, trainData, swapTestElements)
            divergenceKL = updateDKL
    pdb.set_trace()
    print ("Done")
    

def swapDataFromDict(data1, data2, swapList):
    for entry in swapList:
        data1.pop(entry[0], entry[1])
        data2[entry[0]] = entry[1]
            
def swapDistributions(trainData, trainLabelList, trainCountList, trainPriorList,\
                      trainCount, testData, testLabelList, testCountList, \
                        testPriorList, testCount):
    global RANDOM_SWAPS
    # Peform random swaps for improving Kullback-Leibler distacne
    trainKeyValueList = []
    testKeyValueList = []
    trainFileNameList = list(trainData.keys())
    testFileNameList = list(testData.keys())
    updateTrainCountList = copy.deepcopy(trainCountList)
    updateTestCountList = copy.deepcopy(testCountList)
    updateTrainPriorList = copy.deepcopy(trainPriorList)
    updateTestPriorList = copy.deepcopy(testPriorList)
    for i in range(RANDOM_SWAPS):
        # Swap from train data
        trainFileName = trainFileNameList[i]
        trainLabel = trainData[trainFileName]

        for label in trainLabel:
            labelIndex = trainLabelList.index(label)
            updateTrainCountList[labelIndex] -= 1
            updateTestCountList[labelIndex] += 1
            updateTrainPriorList[labelIndex] = \
                updateTrainCountList[labelIndex]/float(trainCount)
            updateTestPriorList[labelIndex] = \
                updateTestCountList[labelIndex]/float(testCount)
        trainKeyValueList.append([trainFileName, trainLabel])
    
        testFileName = testFileNameList[i]
        testLabel = testData[testFileName]

        for label in trainLabel:
            labelIndex = testLabelList.index(label)
            updateTestCountList[labelIndex] += 1
            updateTrainCountList[labelIndex] -= 1
            updateTestPriorList[labelIndex] = \
                updateTestCountList[labelIndex]/float(testCount)
            updateTestPriorList[labelIndex] = \
                updateTrainCountList[labelIndex]/float(trainCount)
        testKeyValueList.append([testFileName, testLabel])

    return trainKeyValueList, updateTrainPriorList, testKeyValueList, \
      updateTestPriorList

updateSplits()
