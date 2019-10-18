#from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#import pyqtgraph.opengl as gl
#import numpy as np
#import pyqtgraph as pg
#import sys
#import h5py;

from PyQt5.QtGui import * #contains QMainWindow

#Window
#contains buttons and drop down menu
#python terminal
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'YawOttSee LIDAR Viewer'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 600
        self.initUI()
        #self.mainWidget = Widget()
        #print(self.mainWidget)
        #self.setCentralWidget(self.mainWidget)
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolsMenu = mainMenu.addMenu('Tools')