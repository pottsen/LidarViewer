from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg
import sys
from atom.api import Atom, Float, Value, observe, Coerced, Int, Typed
import h5py;


#Start building rest of funtionality
class Plot(gl.GLScatterPlotItem):
    def __init__(self, data, size, color):
        super().__init__()
        #gl.GLScatterPlotItem(pos = np.array([[0, 0, 0]]), color = np.array([0,0,0,1]))
    #def addData(self, data, size, color):
        gl.GLScatterPlotItem(pos = data, size = size, color=color)

class Grid(gl.GLGridItem):
    def __init__(self):
        super().__init__()
        gl.GLGridItem()

class Axis(gl.GLAxisItem):
    def __init__(self, size):
        super().__init__()
        gl.GLAxisItem(size = size)

    

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
    
class Widget(gl.GLViewWidget):
    def __init__(self, parent = None):
        #super().__init__()
        gl.GLViewWidget.__init__(self, parent = parent)

class importData():
    def __init__(self):
        pass
    def dataFetch(self, fileName):
        file = h5py.File(fileName, "r")
        xyz = file['/Points/XYZ'][()]
        xyz = np.array(xyz)
        print(fileName, " has ", xyz.size/3, " points.")
        return xyz

app = pg.QtGui.QApplication([])

importData = importData()
xyz1 = importData.dataFetch('Gun1_2.h5')
xyz2 = importData.dataFetch('Gun1_3.h5')
xyz3 = importData.dataFetch('Gun1_4.h5')
xyz = np.concatenate([xyz1, xyz2, xyz3])

foo = Window()
widg = Widget()

color = [0, 1, 1, 0.5]
size = 3

plot = Plot(xyz, size, color)
#plot.addData(xyz, size, color)
grid = Grid()
axis = Axis(pg.Vector(5,5,5))

widg.addItem(grid)
widg.addItem(axis)
widg.addItem(plot)

foo.setCentralWidget(widg)
foo.show()
pg.QtGui.QApplication.exec_()
#sys.exit(app.exec_())
"""    
if __name__ == '__main__':
    #app = QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
"""