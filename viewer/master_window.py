import window as SDW
import ICP_window as AlgnW
from PyQt5 import QtWidgets, QtCore, QtGui
from canvas import Canvas
import vispy.app
import sys

class Window(QtWidgets.QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.initInterface()

    def initInterface(self):
        self.snow_depth_window = SDW.Window()
        self.alignment_window = AlgnW.Window()

        self.window_widgets = QtWidgets.QTabWidget()
        self.window_widgets.addTab(self.alignment_window, "Alignment")
        self.window_widgets.addTab(self.snow_depth_window, "Snow Depth")
        self.setCentralWidget(self.window_widgets)
