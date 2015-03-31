from pylab import *
import normalize as nl
import pdb
import fnmatch
import os
import parser

featureData = []
labelData = []

def featureExtraction(f):
    global featureData, labelData
    # Update to read all training files
    
    basename = f[f.rfind('/') + 1:f.rfind('.')]
    path = f[:f.rfind('/') + 1]
    lg_file = path + 'lg/' + basename + '.lg'        
    csv_file = path + 'csv/' + basename + '.csv'
    
    coordinates = nl.readFile(csv_file) 
    symbolList, labelList = getStrokeIds(lg_file)
    #symbolList = [['0'], ['1'], ['2', '3'], ['4']]
    #labelList = ['q', 'h', '+', 'c']
    print(symbolList)
    print(labelList)
    for i in range(len(symbolList)):
        symbol = symbolList[i]
        resampleCoordinates = nl.resampleSymbol(coordinates, symbol)
        normalCoordinates = nl.widthNormalizeStroke(resampleCoordinates, symbol)
        #pdb.set_trace()
        for key in normalCoordinates.keys():
            # Add normalized distance as feature
            normalCoordinates[key] = \
                calculateStrokeEdgeDistance(normalCoordinates[key])
            # Add curvature angle as feature
            normalCoordinates[key] = \
              getCurvatureFeature(normalCoordinates[key])
            
        #pdb.set_trace()
        pointList = []
        keyList = list(normalCoordinates.keys())
        keyList.sort(key = int)
        for j in range(len(keyList)):
            key = keyList[j]
            for k in range(len(normalCoordinates[key])):
                pointList += normalCoordinates[key][k]
        #pdb.set_trace()
        featureList = createAllFeatures(pointList)
        featureData.append(featureList)
        labelData.append(labelList[i])
    
    #pdb.set_trace()
    # Delete this
    #print (featureData)
    #print (labelData)
    return featureData, labelData
    
def getStrokeIds(fileName):
    symbolList, labelList = [], []
    inputFile = open(fileName, 'rU', newline = '\n')
    for line in inputFile:
        words = [x.strip() for x in line.split(',')]
        if words[0] == 'O':
            symbolList.append(words[4:])
            labelList.append(words[2])
        
    return symbolList, labelList

def createAllFeatures(pointList):
    print ("Fix this to create all the features for data points")
    return pointList

def calculateStrokeEdgeDistance(stroke):
    updatedStroke = []
    firstPoint = stroke[0]
    lastPoint = stroke[len(stroke) - 1]
    for i in range(len(stroke)):
        point = [stroke[i][0], stroke[i][1]]
        numerator = abs(nl.eucledianDist(point, firstPoint) - nl.eucledianDist \
                         (point, lastPoint))
        denominator = abs(nl.eucledianDist(firstPoint, lastPoint))
        normalizedDist = 1 - (numerator / denominator)
        point.append(normalizedDist)
        updatedStroke.append(point)
    return updatedStroke

def getCurvatureFeature(stroke):
    # Point 1, 2, 3
    point1 = [stroke[0][0], stroke[0][1]]
    point2 = [stroke[1][0], stroke[1][1]]
    point3 = [stroke[2][0], stroke[2][1]]

    #stroke[0].append(calculateCurvatureAngle(point1, point1, point2))
    stroke[0].append(0)
    stroke[1].append(calculateCurvatureAngle(point1, point2, point3))
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
    
    stroke[index + 1].append(calculateCurvatureAngle(point1, point2, point3))
    #stroke[index + 2].append(calculateCurvatureAngle(point2, point3, point3))
    stroke[index + 2].append(0.0)
    return stroke




def calculateCurvatureAngle(prevPoint, point, nextPoint):
    #pdb.set_trace()
    vector1 = array([point[0] - prevPoint[0], point[1] - prevPoint[1]])
    vector2 = array([nextPoint[0] - point[0], nextPoint[1] - point[1]])
    angle = arccos(dot(vector1, vector2)/sqrt(dot(vector1, vector1) * dot(vector2, 
        vector2)))
    #pdb.set_trace()
    return angle

def fileCall():
    global featureData, labelData
    trainingFolderPath = "./TrainINKML_v3/"
##    trainingPaths = [trainingFolderPath + f + "/" for f in os.listdir(trainingFolderPath) if os.path.isdir(trainingFolderPath + f)]
    trainingPaths = [trainingFolderPath + "MfrDB/"]
    print(trainingPaths)
    
    for path in trainingPaths:
        files = [path + f for f in os.listdir(path) if os.path.isfile(path + f) and f.endswith(".inkml")]
        files = [path + 'MfrDB0033.inkml']
        for inkml_file in files:
            print(inkml_file)
            
            basename = inkml_file[inkml_file.rfind('/') + 1:inkml_file.rfind('.')]
            path = inkml_file[:inkml_file.rfind('/') + 1]
            lg_file = path + 'lg/' + basename + '.lg'        
            csv_file = path + 'csv/' + basename + '.csv'
            
            if not os.path.exists(csv_file):
                parser.convertStrokesToCsv(inkml_file)
            if not os.path.exists(lg_file):
                parser.convertInkmlToLg(inkml_file)
            symbolList, labelList = getStrokeIds(lg_file)
        ##    print(symbolList)
        ##    print()
            featureExtraction(inkml_file)
        #pdb.set_trace()
    return featureData, labelData

print(fileCall())

