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
RANDOM_SWAPS = 1000
RANDOM_POINTS = 1

def readAllInputData():
    # Final Data Structures
    fileLabelsData = {}
    labelPriors = {}
    labelCount = 0
    
    trainingFolderPath = "./TrainINKML_v3/"
    trainingPaths = [trainingFolderPath + f + "/" for f in os.listdir(trainingFolderPath) if os.path.isdir(trainingFolderPath + f)]
    # For a specific folder
    # trainingPaths = [trainingFolderPath + "extension/"]
    
    for i in range(len(trainingPaths)):
    #for i in range(6):
        path = trainingPaths[i]
        files = [path + f for f in os.listdir(path) if os.path.isfile(path + f) and f.endswith(".inkml")]
        # for a specific file in that folder
        # files = [path + 'MfrDB0033.inkml']
        for inkml_file in files:
            print('Start processing :', inkml_file)
                
            basename = inkml_file[inkml_file.rfind('/') + 1:inkml_file.rfind('.')]
            path = inkml_file[:inkml_file.rfind('/') + 1]
            #lg_file = path + 'lg/' + basename + '.lg'        
            inkmlFile = path + basename + '.inkml'        
            csv_file = path + 'csv/' + basename + '.csv'
            
            if not os.path.exists(csv_file):
                parser.convertStrokesToCsv(inkml_file)
            #if not os.path.exists(lg_file):
            #    parser.convertInkmlToLg(inkml_file)

            # Dictionary which contains the list of symbols which are present
            # in csv_files
            symbolList, labelList = feat.getStrokeIds(inkmlFile)
            fileLabelsData[csv_file] = labelList
            for label in labelList:
                if label not in labelPriors:
                    labelPriors[label] = 1
                else:
                    labelPriors[label] += 1
            labelCount += 1
            
        #pdb.set_trace()
    print ("Total Number of Symbols in the dataset", len(labelPriors.keys()))
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
    for key in labelPriors:
        testPriors[key] = 0
    testCount = 0
    for i in range(testSize):
        randomIndex = randrange(0, len(fileLabelData))
        fileName = fileNameList[i]
        labelList = fileLabelData[fileName]
        testData[fileName] = labelList
        for label in labelList:
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
    print (divergenceKL)
    print ("###############################")
    #pdb.set_trace()
    for i in range(RANDOM_SWAPS):
        swapTrainElements, swapTrainList, swapTestElements, swapTestList = \
            swapDistributions(trainData, \
            trainLabelList, trainCountList, trainPriorList, trainCount,
             testData, testLabelList, testCountList, testPriorList, testCount)
        #pdb.set_trace()
        print ("###############################")
        print ("KL Divergence after swap", i + 1)

        #if i > 0:
        #    print (scipy.stats.entropy(swapTrainList, prevTrainList))
        updateDKL = scipy.stats.entropy(swapTrainList, dataPriorList)
        prevTrainList = swapTrainList
        print (updateDKL)
        print ("###############################")
        if (updateDKL < divergenceKL):
            print ("Update Sample")
            swapDataFromDict(trainData, testData, swapTrainElements)
            swapDataFromDict(testData, trainData, swapTestElements)
            divergenceKL = updateDKL
    #pdb.set_trace()

    # Debug
    print ("###############################")
    print ("Train test check")
    print ("Name of file which is coommon in training and test data")
    print ("* There should not be any such file")
    for trainfile in trainData:
        if trainfile in testData:
            print (trainfile)
    print ("###############################")
    return trainData, testData
    print ("Done")
    

def swapDataFromDict(data1, data2, swapList):
    for entry in swapList:
        data1.pop(entry[0], entry[1])
        data2[entry[0]] = entry[1]
            
def swapDistributions(trainData, trainLabelList, trainCountList, trainPriorList,\
                      trainCount, testData, testLabelList, testCountList, \
                        testPriorList, testCount):
    global RANDOM_POINTS
    # Peform random swaps for improving Kullback-Leibler distacne
    trainKeyValueList = []
    testKeyValueList = []
    trainFileNameList = list(trainData.keys())
    testFileNameList = list(testData.keys())
    updateTrainCountList = copy.deepcopy(trainCountList)
    updateTestCountList = copy.deepcopy(testCountList)
    updateTrainPriorList = copy.deepcopy(trainPriorList)
    updateTestPriorList = copy.deepcopy(testPriorList)
    for j in range(RANDOM_POINTS):
        i = randrange(0, len(trainFileNameList))
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

        i = randrange(0, len(testFileNameList))
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

#updateSplits()
