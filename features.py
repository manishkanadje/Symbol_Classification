###############################################################################
## features.py
##     Used to extract features from data
##
## Submitted by: Manish Kanadje, Kedarnath Calangutkar
###############################################################################

import os
import numpy
import math

import normalize as nl

from xml.dom import minidom

dataIndex = 0
FEATURE_NUMBER = 7

def featureExtraction(csv_file, symbolList, labelList):
    global dataIndex
    # Update to read all training files
    featureData = []
    labelData = []
    
    coordinates = nl.readFile(csv_file)

    for key in coordinates:
        coordinates[key] = nl.duplicatePointRemoval(coordinates[key])

    for i in range(len(symbolList)):
        symbol = symbolList[i]

        # Ensure that the symbol is not just one point
        if (validSymbol(symbol, coordinates)):
            resampleCoordinatesList = nl.resampleSymbol(coordinates, symbol)
    
            normalCoordinatesList = \
                nl.widthNormalizeStroke(resampleCoordinatesList)
            
            # Add normalized distance as feature
            nsedAddedList = \
                    calculateStrokeEdgeDistance(normalCoordinatesList)
            
            # Add curvature angle as feature
            angleAddedList = \
                    getCurvatureFeature(nsedAddedList)
            
            # Add distance from center (both x and y differences) as feature
            diffCenterAddedList = getDifferenceFromCenter(nsedAddedList)

            finalFeatureList = diffCenterAddedList
            pointList = []
            for feature in finalFeatureList:
                pointList += feature
            
            featureList = pointList
            featureData.append(featureList)
            
            if len(labelList) != 0:
                labelData.append(labelList[i])
            
            dataIndex += 1
        else:
            global FEATURE_NUMBER
            featureList = [0.0 for j in range(nl.RESAMPLE_POINTS * FEATURE_NUMBER)]
            featureData.append(featureList)
            if (len(labelList) != 0):
                labelData.append(labelList[i])
        
    return featureData, labelData
    
def validSymbol(symbol, coordinates):
    flag = True
    if (len(symbol) == 1):
        for point in symbol:
            if (len(coordinates[point]) <= 1):
                flag = False
    return flag


def getStrokeIds(fileName):
    xmldoc = minidom.parse(fileName)
    itemlist = xmldoc.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    for tGroup in itemlist:
        labelList.append(tGroup.getElementsByTagName('annotation')[0].firstChild.nodeValue)
        
        strokes = tGroup.getElementsByTagName('traceView')
        strokeList = []
        for stroke in strokes:
            strokeList.append(stroke.attributes["traceDataRef"].nodeValue)
        symbolList.append(strokeList)
    return symbolList, labelList

def getStrokeIdsForTest(fileName):
    xmldoc = minidom.parse(fileName)
    itemlist = xmldoc.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    for tGroup in itemlist:
        strokes = tGroup.getElementsByTagName('traceView')
        strokeList = []
        for stroke in strokes:
            strokeList.append(stroke.attributes["traceDataRef"].nodeValue)
        symbolList.append(strokeList)
    return symbolList, labelList

def calculateStrokeEdgeDistance(stroke):
    firstPoint = stroke[0]
    lastPoint = stroke[len(stroke) - 1]
    for i in range(len(stroke)):
        point = [stroke[i][0], stroke[i][1]]
        numerator = abs(nl.eucledianDist(point, firstPoint) - nl.eucledianDist \
                         (point, lastPoint))
        denominator = abs(nl.eucledianDist(firstPoint, lastPoint))
        # Considers the case where stroke length is 0
        if (denominator != 0):
            normalizedDist = 1 - (numerator / denominator)
        else:
            normalizedDist = 0
        stroke[i].append(normalizedDist)
    return stroke

def getCurvatureFeature(stroke):
    # Point 1, 2, 3
    point1 = [stroke[0][0], stroke[0][1]]
    point2 = [stroke[1][0], stroke[1][1]]
    point3 = [stroke[2][0], stroke[2][1]]

    stroke[0].append(0.0)
    stroke[1].append(0.0)
    for i in range(2, len(stroke) - 2):
        prevPoint = [stroke[i - 2][0], stroke[i - 2][1]]
        point = [stroke[i][0], stroke[i][1]]
        nextPoint = [stroke[i + 2][0], stroke[i + 2][1]]
        angle = calculateCurvatureAngle(prevPoint, point, nextPoint)
        stroke[i].append(angle)
    # Last 3 points
    index = len(stroke) - 3
    point1 = [stroke[index][0], stroke[index][1]]
    point2 = [stroke[index + 1][0], stroke[index + 1][1]]
    point3 = [stroke[index + 2][0], stroke[index + 2][1]]
    
    stroke[index + 1].append(0.0)
    stroke[index + 2].append(0.0)
    return stroke


def calculateCurvatureAngle(prevPoint, point, nextPoint):
    vector1 = numpy.array([point[0] - prevPoint[0], point[1] - prevPoint[1]])
    vector2 = numpy.array([nextPoint[0] - point[0], nextPoint[1] - point[1]])
    numerator = numpy.dot(vector1, vector2)
    denominator = numpy.sqrt(numpy.dot(vector1, vector1) * numpy.dot(vector2, vector2))
    value = numerator/denominator
    if value > 1:
        value = 1
    if value < -1:
        value = -1
    angle = numpy.arccos(value)
    if (numpy.isnan(angle)):
        angle = math.pi
    return angle

def getDifferenceFromCenter(stroke):
    middleIndex = nl.RESAMPLE_POINTS/2
    middlePoint = stroke[int(middleIndex)]
    for point in stroke:
        point.append(point[0] - middlePoint[0])
        point.append(point[1] - middlePoint[1])
    return stroke

def getDifferenceFromOrigin(stroke):
    origin = [0.0, 0.0]
    distanceList = []
    solutionStroke = []
    for point in stroke:
        tempPoint = [point[0], point[1]]
        distance = nl.eucledianDist(origin, tempPoint)
        distanceList.append(distance)
    count = len(distanceList)
    for i in range(count):
        elementIndex = distanceList.index(min(distanceList))
        temp = distanceList.pop(elementIndex)
        element = stroke.pop(elementIndex)
        solutionStroke.append(element)
    return solutionStroke

