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

            
def widthNormalizeStroke(coordinatesList):
    normalCoordinatesList = []
    xCord = []
    yCord = []
    for coord in coordinatesList:
        xCord.append(coord[0])
        yCord.append(coord[1])    
    yMin = min(yCord)
    yMax = max(yCord)
    xMin = min(xCord)
    xMax = max(xCord)
    maxYDiff = yMax - yMin
    maxXDiff = xMax - xMin

    if maxYDiff == 0:
        maxYDiff = 1
    if maxXDiff == 0:
        maxXDiff = 1
    aspectRatio = (maxXDiff)/float(maxYDiff)
    expectedYValue = 1
    expectedXValue = aspectRatio * expectedYValue
    for i in range(len(coordinatesList)):
        newX= expectedXValue - ((xMax - coordinatesList[i][0]) * \
                expectedXValue / maxXDiff)
        newY= (yMax - coordinatesList[i][1]) * \
                expectedYValue / maxYDiff
        normalCoordinatesList.append([newX, newY, coordinatesList[i][2]])

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
    return normalCoordinatesList

def smoothing(fileName):
    figure = scipy.ndimage.imread(fileName + '.png')
    figure = figure[:,:,1]
    figure = scipy.ndimage.gaussian_filter(figure, sigma = 2)
    #savefig(fileName + '_gaussian.png', bbox_inches = 'tight', pad_inches = 0)

def resampleSymbol(coordinates, strokeList):
    numberElements = len(strokeList)
    symbolList = []
    pointToStroke = {}
    strokeList.sort(key = int)
    for stroke in strokeList:
        symbolList += coordinates[stroke]
        for point in coordinates[stroke]:
            pointToStroke[str(point[0]) + str(point[1])] = stroke
    resampleCoordinatesList = resamplePoints(symbolList, pointToStroke)
    return resampleCoordinatesList

#def getResampleNumbers(number, lengthMap, totalPoints):
    #global RESAMPLE_POINTS
    #concernedPoints = RESAMPLE_POINTS
    #distributedLength = {}
    #finalLength = 0
    ##pdb.set_trace()
    #for key in lengthMap.keys():
        #if (lengthMap[key] == 1 or lengthMap[key] == 2):
            #distributedLength[key] = lengthMap[key]
            #concernedPoints -= lengthMap[key]
            #totalPoints -= lengthMap[key]
        #else:
            #distributedLength[key] = 0

    ## Update to incoporate for single points strokes symbol
    #if totalPoints != 0:
        #ratio = concernedPoints/totalPoints
        #tempMap = {}
        #for key in lengthMap.keys():
            #if (distributedLength[key] != 1 and distributedLength[key] != 2):
                #tempMap[key] = int(ratio * lengthMap[key])
                #finalLength += int(ratio * lengthMap[key])
    ##pdb.set_trace()
        #differencePoints = concernedPoints - finalLength
        #while (differencePoints != 0):
            #key = random.choice(list(tempMap.keys()))
            #tempMap[key] += 1
            #differencePoints -= 1
        #distributedLength.update(tempMap)
    ##pdb.set_trace()
    #return distributedLength
    
# def getResampleNumbers(number):
#     global RESAMPLE_POINTS
#     complete = int(RESAMPLE_POINTS/number)
#     difference = RESAMPLE_POINTS - complete * number
#     resampleList = [complete for i in range(number)]
#     #pdb.set_trace()
#     for i in range(difference):
#         resampleList[i] += 1
#     return resampleList

def resamplePoints(symbolList, pointToStroke):
    global RESAMPLE_POINTS
    accStrokeLength = []
    accStrokeLength.append(0)
    for i in range(len(symbolList) - 1):
        accStrokeLength.append(accStrokeLength[i] + \
                eucledianDist(symbolList[i], symbolList[i + 1]))
    #resampleDist = int(accStrokeLength[len(accStrokeLength) - 
    #1]/numberResamplePoints)
    resampleDist = accStrokeLength[len(accStrokeLength) - 1]/RESAMPLE_POINTS
    newPointList = []
    # First and Last elements will never be interpolated
    begin = symbolList[0]
    begin.append(1)
    newPointList.append(begin)
    #pdb.set_trace()
    j = 1
    for p in range(1, (RESAMPLE_POINTS - 1)):
        #pdb.set_trace()
        while accStrokeLength[j] < (p * resampleDist):
            j += 1
        interpolationFactor = (p * resampleDist - accStrokeLength[j - 1])/ \
                              (accStrokeLength[j] - accStrokeLength[j - 1])
        newX = symbolList[j - 1][0] + (symbolList[j][0] - \
                                    symbolList[j - 1][0]) * interpolationFactor
        newY = symbolList[j - 1][1] + (symbolList[j][1] - \
                                             symbolList[j - 1][1]) * \
                                             interpolationFactor
        key1 = str(symbolList[j - 1][0]) + str(symbolList[j - 1][1])
        key2 = str(symbolList[j][0]) + str(symbolList[j][1])
        interpolationFlag = -1
        if (pointToStroke[key1] == pointToStroke[key2]):
            interpolationFlag = 1
        newPointList.append([newX, newY, interpolationFlag])
    lastElement = len(symbolList) - 1
    # Consider for list containing one element
    newPointList.append([symbolList[lastElement][0], \
            symbolList[lastElement][1], 1])
    #pdb.set_trace()
    return newPointList

                                             
def eucledianDist(point1, point2):
    xDist = point1[0] - point2[0]
    yDist = point1[1] - point2[1]
    return math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))           

# Connects all the strokes in the symbol and gives a flag of -1 if the point is 
# interpolated and 1 otherwise.
def createConnectedSymbol(coordinates, strokeList):
    return 1


    
#widthNormalizeFile('exp.csv')


