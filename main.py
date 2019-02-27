from makePlot import *
from main_window import *
from data_management import *
from widget import *

"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph.opengl as gl
"""
import numpy as np
import pyqtgraph as pg
import sys
import h5py;

"""
importData = importData()
xyz1 = importData.dataFetch('Gun1_2.h5')
xyz2 = importData.dataFetch('Gun1_3.h5')
xyz3 = importData.dataFetch('Gun1_4.h5')
xyz = np.concatenate([xyz1, xyz2, xyz3])
"""
def main():

    app = pg.QtGui.QApplication([])
    
    data = importData()
    xyz1 = data.dataFetch('Gun1_2.h5')
    xyz2 = data.dataFetch('Gun1_3.h5')
    xyz3 = data.dataFetch('Gun1_4.h5')
    xyz = np.concatenate([xyz1, xyz2, xyz3])
    
    foo = Window()
    widg = Widget()
    
    size = 3

    scatter1 = Plot()
    color1 = [0, 1, 1, 0.5]
    scatter1.plot.setData(pos = xyz, size = size, color=color1)

    """
    #can add data sets seperately with different colors
    scatter2 = Plot()
    color2 = [1, 1, 0, 0.5]
    scatter2.plot.setData(pos = xyz2, size = size, color=color2)
    scatter3 = Plot()
    color3 = [0, 1, 0, 0.5]
    scatter3.plot.setData(pos = xyz3, size = size, color=color3)
    """

    grid = Grid()
    axis = Axis(pg.Vector(5,5,5))

    widg.addItem(grid)
    widg.addItem(axis)
    widg.addItem(scatter1.plot)
    """
    widg.addItem(scatter2.plot)
    widg.addItem(scatter3.plot)
    """
    foo.setCentralWidget(widg)
    foo.show()
    #pg.QtGui.QApplication.exec_()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()