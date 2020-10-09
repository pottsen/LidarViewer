#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *
#import numpy as np
#import pyqtgraph as pg
#import sys
#import h5py;

import pyqtgraph.opengl as gl #gl.GLViewWidget

class Widget(gl.GLViewWidget):
    def __init__(self, parent = None):
        #super().__init__()
        gl.GLViewWidget.__init__(self, parent = parent)