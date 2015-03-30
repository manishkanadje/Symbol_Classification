from pylab import *
from sklearn import svm
import pdb

import normalize as nl
import features as feat

def getTrainingData():
    featureList, labelList = feat.fileCall()
    svmClassifier = svm.SVC()
    svmClassifier.fit(featureList, labelList)
    pdb.set_trace()
    print ("Done Training")

getTrainingData()
