from pylab import *
import csv
import scipy.ndimage
from scipy import misc
import pdb
from PIL import Image
import random

RESAMPLE_POINTS = 30

debugCount = 0

def readFile(fileName):
    inputFile = open(fileName, 'rU', newline = '\n')
    csvReader = csv.reader(inputFile, delimiter = ',')
    coordinates = {}
    for line in csvReader:
        coordinates[line[0]] = []
        for i in range(len(line) - 1):
            lineList = line[i + 1].split(" ")
            coordinates[line[0]].append([float(lineList[0]), float(lineList[1])])
    return coordinates


def duplicatePointRemoval(inputPoints):
    containerMap = {}
    outputPoints = []
    for point in inputPoints:
        key = str(point[0]) + str(point[1])
        if key not in containerMap:
            outputPoints.append(point)
        containerMap[key] = 1
    return outputPoints


            
def widthNormalizeStroke(coordinates, strokeList):
    
    xCord = []
    yCord = []
    for id in strokeList:
        for coord in coordinates[id]:
            xCord.append(coord[0])
            yCord.append(coord[1])    
    yMin = min(yCord)
    yMax = max(yCord)
    xMin = min(xCord)
    xMax = max(xCord)
    maxYDiff = yMax - yMin
    maxXDiff = xMax - xMin

    if maxYDiff == 0:
        pdb.set_trace()
        
    aspectRatio = (xMax - xMin)/float((yMax - yMin))
    expectedYValue = 1
    expectedXValue = aspectRatio * expectedYValue
    newCoordinates = {}
    for key in strokeList:
        newCoordinates[key] = []
        for i in range(len(coordinates[key])):
            newX= xMax - ((xMax - coordinates[key][i][0]) * \
            expectedXValue / maxXDiff)
            newY= (yMax - coordinates[key][i][1]) * \
            expectedYValue / maxYDiff
            newCoordinates[key].append([newX, newY])

    # if (strokeList[0] == '7'):
    #     pdb.set_trace()

    # Create an image file
    #pdb.set_trace()
    # figure()
    # for key in strokeList:
    #     for point in newCoordinates[key]:
    #         plot(point[0], point[1], '.k', markersize = 10)
    # axis('off')
    #show()
    #fileName = fileName[:fileName.find('.')]
    #pdb.set_trace()
    #fileName = 'test'
    #savefig(fileName + strokeList[0] + '.png', bbox_inches = 'tight', pad_inches = 0)
    #close()
    #smoothing(fileName)
    return newCoordinates

def smoothing(fileName):
    figure = scipy.ndimage.imread(fileName + '.png')
    figure = figure[:,:,1]
    figure = scipy.ndimage.gaussian_filter(figure, sigma = 2)
    #savefig(fileName + '_gaussian.png', bbox_inches = 'tight', pad_inches = 0)

def resampleSymbol(coordinates, strokeList):
    numberElements = len(strokeList)
    newCoordinates = {}
    lengthMap = {}
    totalPoints = 0.0
    for stroke in strokeList:
        newCoordinates[stroke] = coordinates[stroke]
        lengthMap[stroke] = len(coordinates[stroke])
        totalPoints += len(coordinates[stroke])
    resamplePointMap = getResampleNumbers(numberElements, lengthMap, totalPoints)
    resampleCoordinates = resamplePoints(newCoordinates, resamplePointMap)

    return resampleCoordinates

def getResampleNumbers(number, lengthMap, totalPoints):
    global RESAMPLE_POINTS
    concernedPoints = RESAMPLE_POINTS
    distributedLength = {}
    finalLength = 0
    #pdb.set_trace()
    for key in lengthMap.keys():
        if (lengthMap[key] == 1 or lengthMap[key] == 2):
            distributedLength[key] = lengthMap[key]
            concernedPoints -= lengthMap[key]
            totalPoints -= lengthMap[key]
        else:
            distributedLength[key] = 0

    # Update to incoporate for single points strokes symbol
    if totalPoints != 0:
        ratio = concernedPoints/totalPoints
        tempMap = {}
        for key in lengthMap.keys():
            if (distributedLength[key] != 1 and distributedLength[key] != 2):
                tempMap[key] = int(ratio * lengthMap[key])
                finalLength += int(ratio * lengthMap[key])
    #pdb.set_trace()
        differencePoints = concernedPoints - finalLength
        while (differencePoints != 0):
            key = random.choice(list(tempMap.keys()))
            tempMap[key] += 1
            differencePoints -= 1
        distributedLength.update(tempMap)
    #pdb.set_trace()
    return distributedLength
    
# def getResampleNumbers(number):
#     global RESAMPLE_POINTS
#     complete = int(RESAMPLE_POINTS/number)
#     difference = RESAMPLE_POINTS - complete * number
#     resampleList = [complete for i in range(number)]
#     #pdb.set_trace()
#     for i in range(difference):
#         resampleList[i] += 1
#     return resampleList

def resamplePoints(coordinates, pointsMap):
    global debugCount
    newCoordinates = {}

    for key in coordinates.keys():
        numberResamplePoints = pointsMap[key]

        if numberResamplePoints == 0:
            pdb.set_trace()
        accStrokeLength = []
        accStrokeLength.append(0)
        for i in range(len(coordinates[key]) - 1):
            accStrokeLength.append(accStrokeLength[i] + \
                        eucledianDist(coordinates[key][i], \
                            coordinates[key][i + 1]))
        #resampleDist = int(accStrokeLength[len(accStrokeLength) - 
        #1]/numberResamplePoints)
        resampleDist = accStrokeLength[len(accStrokeLength) - 
        1]/numberResamplePoints
        newPointList = []
        begin = coordinates[key][0]
        newPointList.append(begin)
        #pdb.set_trace()
        j = 1
        for p in range(1, (numberResamplePoints - 1)):
            #pdb.set_trace()
            debugCount += 1
            while accStrokeLength[j] < (p * resampleDist):
                j += 1
            interpolationFactor = (p * resampleDist - accStrokeLength[j - 1])/ \
                (accStrokeLength[j] - accStrokeLength[j - 1])
            newX = coordinates[key][j - 1][0] + (coordinates[key][j][0] - \
                                                 coordinates[key][j - 1][0]) * \
                                                 interpolationFactor
            newY = coordinates[key][j - 1][1] + (coordinates[key][j][1] - \
                                                 coordinates[key][j - 1][1]) * \
                                                 interpolationFactor
            newPointList.append([newX, newY])

        
        lastElement = len(coordinates[key]) - 1
        # Consider for list containing one element
        if (lastElement > 0):
            newPointList.append([coordinates[key][lastElement][0], \
                                coordinates[key][lastElement][1]])
        newCoordinates[key] = newPointList
    #pdb.set_trace()
    return newCoordinates

                                             
def eucledianDist(point1, point2):
    xDist = point1[0] - point2[0]
    yDist = point1[1] - point2[1]
    return math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))           




    
#widthNormalizeFile('exp.csv')

