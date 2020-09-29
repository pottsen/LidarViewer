import depth_window as SDW
import alignment_window as AW
import cropping_window as CW
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
        self.alignment_window = AW.Window()
        self.cropping_window = CW.Window()

        self.window_widgets = QtWidgets.QTabWidget()
        self.window_widgets.addTab(self.cropping_window, "Crop")
        self.window_widgets.addTab(self.alignment_window, "Alignment")
        self.window_widgets.addTab(self.snow_depth_window, "Snow Depth")
        self.setCentralWidget(self.window_widgets)
