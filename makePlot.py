# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# import pyqtgraph as pg
# import sys
# import h5py;

import numpy as np
import pyqtgraph.opengl as gl

class Plot():
    def __init__(self):
        self.plot = gl.GLScatterPlotItem(pos=np.array([[0,0,0]]), color=np.array([0,0,0,1]))

class Grid(gl.GLGridItem):
    def __init__(self):
        super().__init__()
        gl.GLGridItem()

class Axis(gl.GLAxisItem):
    def __init__(self, size):
        super().__init__()
        gl.GLAxisItem(size = size)