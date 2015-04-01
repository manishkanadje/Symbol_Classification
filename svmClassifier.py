from pylab import *
from sklearn import svm
import pdb

import normalize as nl
import features as feat

def getTrainingData():
    featureList, labelList = feat.fileCall()
    #pdb.set_trace()
    svmClassifier = svm.SVC()
    svmClassifier.fit(featureList, labelList)
    results = svmClassifier.predict(featureList)
    count  = 0
    for i in range(len(results)):
        if (results[i] == labelList[i]):
            count += 1
    print (count/len(labelList))
    pdb.set_trace()
    print ("Done Training")

getTrainingData()

