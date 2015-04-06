###############################################################################
## normalize.py
##     module to resample a symbol to a total of 30 points
##
## Submitted by: Manish Kanadje, Kedarnath Calangutkar
###############################################################################

import csv
import random
import math
import scipy.ndimage

from scipy import misc
from PIL import Image

RESAMPLE_POINTS = 30

# Reads the csv file and creates a dictionary of coordinates belonging to each stroke
def readFile(fileName):
    inputFile = open(fileName, 'rU')
    csvReader = csv.reader(inputFile, delimiter = ',')
    coordinates = {}
    for line in csvReader:
        coordinates[line[0]] = []
        for i in range(len(line) - 1):
            lineList = line[i + 1].split(" ")
            coordinates[line[0]].append([float(lineList[0]), float(lineList[1])])
    return coordinates

# Removes the duplicate points from the given list of coordinates
def duplicatePointRemoval(inputPoints):
    containerMap = {}
    outputPoints = []
    for point in inputPoints:
        key = str(point[0]) + ',' + str(point[1])
        if key not in containerMap:
            outputPoints.append(point)
        containerMap[key] = 1
    return outputPoints

# Normalizes the given list of coordinates. Y coodinates is scaled within 0 and 1. X coordinate is scaled based on the original aspect ratio of the symbol.
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

    return normalCoordinatesList

# Resmaples symbol represented by strokeList into a single list containing 30 points for each symbol.
def resampleSymbol(coordinates, strokeList):
    numberElements = len(strokeList)
    symbolList = []
    pointToStroke = {}
    strokeList.sort(key = int)
    for stroke in strokeList:
        symbolList += coordinates[stroke]
        for point in coordinates[stroke]:
            pointToStroke[str(point[0]) + ',' + str(point[1])] = stroke
    resampleCoordinatesList = resamplePoints(symbolList, pointToStroke)
    return resampleCoordinatesList

# Implementation of interpolation algorithm for resmapling the symbol into 30 points. If the point does not exist in the original stroke it has a new attribute valued -1 otherwise 1.
def resamplePoints(symbolList, pointToStroke):
    global RESAMPLE_POINTS
    accStrokeLength = []
    accStrokeLength.append(0)
    for i in range(len(symbolList) - 1):
        accStrokeLength.append(accStrokeLength[i] + \
                eucledianDist(symbolList[i], symbolList[i + 1]))
    resampleDist = accStrokeLength[len(accStrokeLength) - 1]/RESAMPLE_POINTS
    newPointList = []
    # First and Last elements will never be interpolated
    begin = symbolList[0]
    begin.append(1)
    newPointList.append(begin)
    j = 1
    for p in range(1, (RESAMPLE_POINTS - 1)):
        if (len(accStrokeLength) == 1):
            pdb.set_trace()
        while accStrokeLength[j] < (p * resampleDist):
            j += 1
            
        interpolationFactor = (p * resampleDist - accStrokeLength[j - 1])/ \
                              (accStrokeLength[j] - accStrokeLength[j - 1])
        newX = symbolList[j - 1][0] + (symbolList[j][0] - \
                                    symbolList[j - 1][0]) * interpolationFactor
        newY = symbolList[j - 1][1] + (symbolList[j][1] - \
                                             symbolList[j - 1][1]) * \
                                             interpolationFactor
        key1 = str(symbolList[j - 1][0]) + ',' + str(symbolList[j - 1][1])
        key2 = str(symbolList[j][0]) + ',' + str(symbolList[j][1])
        interpolationFlag = -1
        if (pointToStroke[key1] == pointToStroke[key2]):
            interpolationFlag = 1
        newPointList.append([newX, newY, interpolationFlag])
    lastElement = len(symbolList) - 1
    newPointList.append([symbolList[lastElement][0], symbolList[lastElement][1], 1])
    return newPointList

# Calculate the Eucledian distance between point1 and point2.
def eucledianDist(point1, point2):
    xDist = point1[0] - point2[0]
    yDist = point1[1] - point2[1]
    return math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))           

