from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtCore import Qt
import vispy.app
import sys
from grid import Grid

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.grid = Grid()
        self.initInterface()

    def initInterface(self):
        self.setWindowTitle("Lidar Snow Depth Calculator")
        
        self.leftDock = QDockWidget('Data Options', self)
        self.leftDock.setAcceptDrops(False)
        ##### LEFT PANEL WIDGET
        # Set left layout
        self.left_widget_layout = QVBoxLayout()
        
        self.base_file_button = QPushButton("Choose Base File")
        self.base_file_button.clicked.connect(self.click_base_file_button)

        self.snow_file_button = QPushButton("Choose Snow File")
        self.snow_file_button.clicked.connect(self.click_snow_file_button)

        self.run_snowdepth_button = QPushButton("Calculate Snow Depth")
        self.run_snowdepth_button.clicked.connect(self.click_snow_depth_button)

        self.run_alignment_button = QPushButton("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)
        
        self.left_widget_layout.addWidget(self.base_file_button)
        self.left_widget_layout.addWidget(self.snow_file_button)
        self.left_widget_layout.addWidget(self.run_snowdepth_button)
        self.left_widget_layout.addWidget(self.run_alignment_button)

        # Make left widget and add the left layout
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_widget_layout)
        self.leftDock.setWidget(self.left_widget)
        
        ##### BOTTOM TEXT DOCK AND WIDGET
        # TODO: Create Terminal Widget
        self.bottomDock = QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        # self.bottomDock.setAllowedAreas(BottomDockWidgetArea)
        self.message_window = QTextBrowser()
        self.bottomDock.setWidget(self.message_window)

        
        ##### MAIN PLOT WIDGET
        # Create Tab widget for plots
        self.plot_widgets = QTabWidget()
        self.plot_widgets.tabBar().setObjectName("mainTab")

        self.setCentralWidget(self.plot_widgets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDock)
        
    def update(self):
        pass


    def click_base_file_button(self):
        self.base_file_path = get_file()
        self.message_window.append("Cleaning and loading base file: " + str(self.base_file_path[0]))
        self.grid.load_base_file(self.base_file_path[0]) 

    def click_snow_file_button(self):
        self.snow_file_path = get_file()
        self.message_window.append("Cleaning and loading snow file: " + str(self.snow_file_path[0]))
        self.grid.load_snow_file(self.snow_file_path[0])

    def click_snow_depth_button(self):
        self.grid.make_grid_by_cell()
        self.message_window.append("Grid made and points added." + str(run_snowdepth()))
        # print("Calculate the depth")

    def click_run_alignment_button(self):
        print("Calculate the depth")

class Canvas(vispy.app.Canvas):
    # resize = pyqtSignal()
    def __init__(self):
        super(Canvas, self).__init__()
        # self.resize.connect(self.resize_widgets())
        self.window = Window()
        
    


# def canvas():
#     canvas = Canvas()
#     canvas.window.show()
#     vispy.app.run()

# canvas()