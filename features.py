from pylab import *
from xml.dom import minidom
import normalize as nl
import pdb
import fnmatch
import os
import parser

#featureData = []
#labelData = []
dataIndex = 0
FEATURE_NUMBER = 7

def featureExtraction(csv_file, symbolList, labelList):
    #global featureData, labelData, dataIndex
    global dataIndex
    # Update to read all training files
    featureData = []
    labelData = []
    #pdb.set_trace()
    #basename = f[f.rfind('/') + 1:f.rfind('.')]
    #path = f[:f.rfind('/')]
    #path = path[:path.rfind('/') + 1]
    #lg_file = path + 'lg/' + basename + '.lg'        
    #lg_file = path + basename + '.inkml'        
    #csv_file = path + 'csv/' + basename + '.csv'
    
    coordinates = nl.readFile(csv_file)
    #if (len(coordinates.keys()) == 1 and '2' in coordinates):
    #    pdb.set_trace()
    #symbolList, labelList = getStrokeIds(lg_file)

    #pdb.set_trace()
    for key in coordinates:
        coordinates[key] = nl.duplicatePointRemoval(coordinates[key])

    for i in range(len(symbolList)):
        symbol = symbolList[i]
        #print (lg_file)

        # Ensure that the symbol is not just one point
        if (validSymbol(symbol, coordinates)):
            #pdb.set_trace()
            resampleCoordinatesList = nl.resampleSymbol(coordinates, symbol)
            #for point in resampleCoordinatesList:
            #    plot(point[0], point[1], '.k', markersize = 10)
    
            normalCoordinatesList = \
                nl.widthNormalizeStroke(resampleCoordinatesList)
            #for point in normalCoordinatesList:
                #plot(point[0], point[1], '.k', markersize = 10)
            #show()
            #pdb.set_trace()
            
            # Add normalized distance as feature
            nsedAddedList = \
                    calculateStrokeEdgeDistance(normalCoordinatesList)
            
            #pdb.set_trace() 
            # Add curvature angle as feature
            angleAddedList = \
                    getCurvatureFeature(nsedAddedList)
            
            #pdb.set_trace()
            diffCenterAddedList = getDifferenceFromCenter(nsedAddedList)

            #originNormalizedList = getDifferenceFromOrigin(diffCenterAddedList)
            
            finalFeatureList = diffCenterAddedList
            pointList = []
            for feature in finalFeatureList:
                pointList += feature
            #pdb.set_trace()
            featureList = createAllFeatures(pointList)
            featureData.append(featureList)
            #pdb.set_trace()
            if len(labelList) != 0:
                labelData.append(labelList[i])
            #print ('Data Index : ', dataIndex)
            dataIndex += 1
        else:
            global FEATURE_NUMBER
            featureList = [0.0 for j in range(nl.RESAMPLE_POINTS * FEATURE_NUMBER)]
            featureData.append(featureList)
            labelData.append(labelList[i])
        
    #pdb.set_trace()
    return featureData, labelData
    
def validSymbol(symbol, coordinates):
    flag = True
    #pdb.set_trace()
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
        #labelList.append(tGroup.getElementsByTagName('annotation')[0].firstChild.nodeValue)
        
        strokes = tGroup.getElementsByTagName('traceView')
        strokeList = []
        for stroke in strokes:
            strokeList.append(stroke.attributes["traceDataRef"].nodeValue)
        symbolList.append(strokeList)
    return symbolList, labelList

def createAllFeatures(pointList):
    #print ("Fix this to create all the features for data points")
    return pointList

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
        #point.append(normalizedDist)
        stroke[i].append(normalizedDist)
    return stroke

def getCurvatureFeature(stroke):
    # Point 1, 2, 3
    point1 = [stroke[0][0], stroke[0][1]]
    point2 = [stroke[1][0], stroke[1][1]]
    point3 = [stroke[2][0], stroke[2][1]]

    #stroke[0].append(calculateCurvatureAngle(point1, point1, point2))
    stroke[0].append(0.0)
    #stroke[1].append(calculateCurvatureAngle(point1, point2, point3))
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
    #stroke[index + 1].append(calculateCurvatureAngle(point1, point2, point3))
    #stroke[index + 2].append(calculateCurvatureAngle(point2, point3, point3))
    stroke[index + 2].append(0.0)
    return stroke


def calculateCurvatureAngle(prevPoint, point, nextPoint):
    #pdb.set_trace()
    vector1 = array([point[0] - prevPoint[0], point[1] - prevPoint[1]])
    vector2 = array([nextPoint[0] - point[0], nextPoint[1] - point[1]])
    numerator = dot(vector1, vector2)
    #print (numerator)
    denominator = sqrt(dot(vector1, vector1) * dot(vector2, vector2))
    #print (denominator)
    value = numerator/denominator
    if value > 1:
        value = 1
    if value < -1:
        value = -1
    angle = arccos(value)
    if (isnan(angle)):
        angle = pi
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

def fileCall():
    global featureData, labelData
    trainingFolderPath = "./TrainINKML_v3/"
    trainingPaths = [trainingFolderPath + f + "/" for f in os.listdir(trainingFolderPath) if os.path.isdir(trainingFolderPath + f)]
    # For a specific folder
    trainingPaths = [trainingFolderPath + "HAMEX/"]
    print(trainingPaths)

    loop = 0
    for i in range(len(trainingPaths)):
    #for i in range(3):
        path = trainingPaths[i]
        files = [path + f for f in os.listdir(path) if os.path.isfile(path + f) and f.endswith(".inkml")]
        # for a specific file in that folder
        files = [path + 'formulaire001-equation002.inkml']
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
            symbolList, labelList = getStrokeIds(lg_file)
            # Debug point
            if (inkml_file 
                =='./TrainINKML_v3/KAIST/KME1G3_0_sub_10.inkml'):
                pdb.set_trace()
            featureExtraction(inkml_file)
            print ("Done Processing :", inkml_file)
        #pdb.set_trace()
    return featureData, labelData

#print(fileCall())


# ans = getStrokeIds("./TrainINKML_v3/HAMEX/formulaire001-equation002.inkml")
# for i in range(len(ans[0])):
    # print(ans[0][i], " - ", ans[1][i])
