from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtCore import Qt
import vispy.app
import sys
from grid import Grid
from data_manager import Manager

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.grid = Grid()
        self.manager = Manager()
        self.initInterface()


    def initInterface(self):
        self.setWindowTitle("Lidar Snow Depth Calculator")
        
        self.leftDock = QDockWidget('Data Options', self)
        self.leftDock.setAcceptDrops(False)
        # self.leftDock.isFloating(False)
        ##### LEFT PANEL WIDGET
        # Set left layout
        self.left_widget_layout = QVBoxLayout()
        self.left_top_widget_layout = QVBoxLayout()
        self.left_bottom_widget_layout = QVBoxLayout()

        ### Left top widget. Buttons to load in data and run algorithms

        self.base_file_button = QPushButton("Load Data")
        self.base_file_button.clicked.connect(self.click_load_file_button)

        self.snow_file_button = QPushButton("Choose Snow File")
        self.snow_file_button.clicked.connect(self.click_snow_file_button)

        self.plot_initial_button = QPushButton("Plot Initial")
        self.plot_initial_button.clicked.connect(self.click_plot_initial_button)

        self.run_alignment_button = QPushButton("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)

        self.flag_vegetation_button = QPushButton("Flag Vegetation and Cliffs")
        self.flag_vegetation_button.clicked.connect(self.click_flag_vegetation_button)

        self.run_snowdepth_button = QPushButton("Calculate Snow Depth")
        self.run_snowdepth_button.clicked.connect(self.click_snow_depth_button)

        self.plot_snowdepth_button = QPushButton("Plot Snow Depth")
        self.plot_snowdepth_button.clicked.connect(self.click_plot_snowdepth_button)

        self.left_top_widget_layout.addWidget(self.base_file_button)
        self.left_top_widget_layout.addWidget(self.snow_file_button)
        self.left_top_widget_layout.addWidget(self.plot_initial_button)
        self.left_top_widget_layout.addWidget(self.run_alignment_button)
        self.left_top_widget_layout.addWidget(self.flag_vegetation_button)
        self.left_top_widget_layout.addWidget(self.run_snowdepth_button)
        self.left_top_widget_layout.addWidget(self.plot_snowdepth_button)

        ### Left bottom widget with radio buttons and file paths
        # self.test_radio_button = QRadioButton("Test")
        self.test_radio_button = QCheckBox("Test")
        self.left_bottom_widget_layout.addWidget(self.test_radio_button)
        self.test2_radio_button = QCheckBox("Test2")
        self.left_bottom_widget_layout.addWidget(self.test2_radio_button)
        ### Add left panel widgets to left layout

        # Make left widget and add the left layout
        self.left_widget = QWidget()

        self.left_top_widget = QWidget()
        self.left_top_widget.setLayout(self.left_top_widget_layout)
        self.left_widget_layout.addWidget(self.left_top_widget)

        self.left_bottom_widget = QWidget()
        self.left_bottom_widget.setLayout(self.left_bottom_widget_layout)
        self.left_widget_layout.addWidget(self.left_bottom_widget)

        self.left_widget.setLayout(self.left_widget_layout)
        self.leftDock.setWidget(self.left_widget)
        
        ##### BOTTOM TEXT DOCK AND WIDGET
        # TODO: Create Terminal Widget
        self.bottomDock = QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        # self.bottmDock.isFloating(False)
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


    def click_load_file_button(self):
        self.base_file_path = get_file()
        self.message_window.append("Cleaning and loading file: " + str(self.base_file_path[0]))
        self.grid.load_base_file(self.base_file_path[0]) 
        self.message_window.append(" ")

    def click_snow_file_button(self):
        self.snow_file_path = get_file()
        self.message_window.append("Cleaning and loading snow file: " + str(self.snow_file_path[0]))
        self.grid.load_snow_file(self.snow_file_path[0])
        self.message_window.append(" ")


    def click_plot_initial_button(self):
        self.message_window.append("Plotting scans...")
        self.initial_view = self.grid.plot_points_initial()
        self.plot_widgets.addTab(self.initial_view.native, "Initial Plot")
        self.message_window.append(" ")

    def click_run_alignment_button(self):
        print("Calculate the depth")
        self.message_window.append(" ")

    def click_flag_vegetation_button(self):
        self.message_window.append("Creating grid and adding points.")
        self.grid.make_grid_by_cell()
        self.message_window.append("Complete!")
        self.message_window.append("Flagging cells...")
        count, num_cells = self.grid.flag_vegetation('snow')
        self.message_window.append(str(count) + " out of " + str(num_cells) + " cells with vegetation and/or cliffs.")
        self.message_window.append(" ")

    def click_snow_depth_button(self):
        self.message_window.append("Calculating snow depth...")
        average, maximum, minimum = self.grid.calculate_snow_depth()
        self.message_window.append("Average Depth: " + str(average))
        self.message_window.append("Max Depth: " + str(maximum))
        self.message_window.append("Minimum Depth: " + str(minimum))
        self.message_window.append(" ")

    def click_plot_snowdepth_button(self):
        self.message_window.append("Coloring and plotting.... ")
        self.grid.color_points()
        self.plot_view = self.grid.plot_points()
        self.plot_widgets.addTab(self.plot_view.native, "Snow Depth Plot")
        self.message_window.append(" ")







class Canvas(vispy.app.Canvas):
    # resize = pyqtSignal()
    def __init__(self):
        super(Canvas, self).__init__()
        # self.resize.connect(self.resize_widgets())
        self.window = Window()

    def set_canvas_to_grid(self):
        return self
        
    


# def canvas():
#     canvas = Canvas()
#     canvas.window.show()
#     vispy.app.run()

# canvas()