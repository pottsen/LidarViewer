import depth_window as SDW
import alignment_window as AW
import cropping_window as CW
from PyQt5 import QtWidgets, QtCore, QtGui
from file_manager import File_Manager
import vispy.app
import sys

"""
Master window initializes and holds all the other windows. Creates connections to the master file manager as well
"""
class Window(QtWidgets.QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Lidar Snow Depth Calculator")
        self.file_manager = File_Manager()
        self.initInterface()

    def initInterface(self):
        self.snow_depth_window = SDW.Window(self.file_manager)
        self.alignment_window = AW.Window(self.file_manager)
        self.cropping_window = CW.Window(self.file_manager)

        self.window_widgets = QtWidgets.QTabWidget()
        self.window_widgets.addTab(self.cropping_window, "Crop")
        self.window_widgets.addTab(self.alignment_window, "Alignment")
        self.window_widgets.addTab(self.snow_depth_window, "Snow Depth")
        self.setCentralWidget(self.window_widgets)
