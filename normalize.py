from pylab import *
import csv
import scipy.ndimage
from scipy import misc
import pdb
from PIL import Image

RESAMPLE_POINTS = 30

def readFile(fileName):
    inputFile = open(fileName, 'rU', newline = '\n')
    csvReader = csv.reader(inputFile, delimiter = ',')
    coordinates = {}
    for line in csvReader:
        coordinates[line[0]] = []
        for i in range(len(line) - 2):
            lineList = line[i + 1].split(" ")
            coordinates[line[0]].append([float(lineList[0]), float(lineList[1])])
    return coordinates

            
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

    if (strokeList[0] == '7'):
        pdb.set_trace()

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
    for stroke in strokeList:
        newCoordinates[stroke] = coordinates[stroke]
    resamplePointList = getResampleNumbers(numberElements)
    resampleCoordinates = resamplePoints(newCoordinates, resamplePointList)

    return resampleCoordinates

def getResampleNumbers(number):
    global RESAMPLE_POINTS
    complete = int(RESAMPLE_POINTS/number)
    difference = RESAMPLE_POINTS - complete * number
    resampleList = [complete for i in range(number)]
    #pdb.set_trace()
    for i in range(difference):
        resampleList[i] += 1
    return resampleList

def resamplePoints(coordinates, pointsList):
    newCoordinates = {}
    pointIndex = 0
    for key in coordinates.keys():
        numberResamplePoints = pointsList[pointIndex]
        #pdb.set_trace()
        pointIndex += 1
        accStrokeLength = []
        accStrokeLength.append(0)
        for i in range(len(coordinates[key]) - 1):
            accStrokeLength.append(accStrokeLength[i] + \
                        eucledianDist(coordinates[key][i], \
                            coordinates[key][i + 1]))
        resampleDist = int(accStrokeLength[len(accStrokeLength) - 
        1]/numberResamplePoints)
        newPointList = []
        begin = coordinates[key][0]
        newPointList.append(begin)
        #pdb.set_trace()
        j = 1
        for p in range(1, (numberResamplePoints - 1)):
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

