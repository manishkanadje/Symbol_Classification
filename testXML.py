import pdb
import pickle
from pylab import *
from sklearn import svm
from sklearn import ensemble
from sklearn.externals import joblib
from xml.dom import minidom
import os
from random import *
from sklearn import metrics

def findSymbol(inkml_parsed, strokeList):
    traceGroups = inkml_parsed.getElementsByTagName('traceGroup')[0].getElementsByTagName('traceGroup')
    symbolList, labelList = [], []
    #pdb.set_trace()
    for tGroup in traceGroups:
        stroke_found = True 
        strokes = tGroup.getElementsByTagName('traceView')
        for stroke in strokes:
            stroke_id = stroke.attributes["traceDataRef"].nodeValue
            if stroke_id not in strokeList:
                stroke_found = False
                break
        if stroke_found:
            pdb.set_trace()
            annotationXML = tGroup.getElementsByTagName('annotationXML')
            symbol = annotationXML[0].attributes["href"].nodeValue
            return symbol.replace(',', 'COMMA')
        
    return None

sList = ['37']
ink = pickle.load(open('inkmlp.p', 'rb'))
findSymbol(ink, sList)
