#from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#import pyqtgraph.opengl as gl
#import pyqtgraph as pg
#import sys

import h5py; #hadles data import/conversion
import numpy as np #allows mathematical operations

class importData():
    def __init__(self):
        pass
    def dataFetch(self, fileName):
        file = h5py.File(fileName, "r")
        xyz = file['/Points/XYZ'][()]
        xyz = np.array(xyz)
        print(fileName, " has ", xyz.size/3, " points.")
        return xyz
