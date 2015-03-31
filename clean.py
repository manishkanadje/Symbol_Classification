import shutil
import os

trainingFolderPath = "./TrainINKML_v3/"
trainingPaths = [trainingFolderPath + f + "/" for f in os.listdir(trainingFolderPath) if os.path.isdir(trainingFolderPath + f)]
for path in trainingPaths:
    if os.path.exists(path + "csv/"):
        shutil.rmtree(path + "csv/")
    if os.path.exists(path + "lg/"):
        shutil.rmtree(path + "lg/")

