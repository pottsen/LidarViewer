from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from data_manager import Manager, file_object

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
        self.left_dock()

        self.bottomDock = QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        self.bottom_dock()

        self.main_panel()

    def left_dock(self):
        self.left_dock_widget_layout = QVBoxLayout()
        self.data_widget_layout = QVBoxLayout()

        """
        Left data widget. Button to load in data and check boxes for files
        """
        self.plot_widget_layout = QVBoxLayout()
        self.load_file_button = QPushButton("Load Data")
        self.load_file_button.clicked.connect(self.click_load_file_button)
        self.data_widget_layout.addWidget(self.load_file_button)

        self.file_box = QWidget()
        self.file_layout = QVBoxLayout()
        
        for i in range(len(self.manager.file_list)):
            self.file_layout.addWidget(self.manager.file_list[i])
        
        self.file_box.setLayout(self.file_layout)
        self.data_widget_layout.addWidget(self.file_box)

        self.data_widget = QWidget()
        self.data_widget.setLayout(self.data_widget_layout)
        self.left_dock_widget_layout.addWidget(self.data_widget)

        """
        Left algorithm widget. Buttons to flag vegetation and calculate snowdepth
        """
        self.alg_widget_layout = QVBoxLayout()
        self.vegetation_button = QPushButton("Find Vegetation and Cliffs")
        self.calculate_snowdepth_button = QPushButton("Calculate Snow Depth")

        self.data_widget_layout.addWidget(self.vegetation_button)
        self.data_widget_layout.addWidget(self.calculate_snowdepth_button)

        self.alg_widget = QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Left plot widget. Has all the plotting options in it.
        """
        self.plot_snowdepth_button = QPushButton("Plot Snow Depth")
        self.plot_snowdepth_button.clicked.connect(self.click_plot_snowdepth_button)
        self.plot_widget_layout.addWidget(self.plot_snowdepth_button)

        self.plot_widget = QWidget()
        self.plot_widget.setLayout(self.plot_widget_layout)
        self.left_dock_widget_layout.addWidget(self.plot_widget)

        """
        Make left dock widget.
        """
        self.left_dock_widget = QWidget()
        self.left_dock_widget.setLayout(self.left_dock_widget_layout)
        self.leftDock.setWidget(self.left_dock_widget)
        
    def bottom_dock(self):
        ##### BOTTOM TEXT DOCK AND WIDGET
        self.message_window = QTextBrowser()
        self.bottomDock.setWidget(self.message_window)

    def main_panel(self):
        ##### MAIN PLOT WIDGET
        # Create Tab widget for plots
        self.plot_widgets = QTabWidget()
        self.plot_widgets.tabBar().setObjectName("mainTab")
        self.setCentralWidget(self.plot_widgets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDock)

    def click_load_file_button(self):
        file_path = get_file()
        self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
        self.manager.add_file(str(file_path[0])) 
        self.message_window.append(" ")
        self.left_dock()

    # def click_plot_initial_button(self):
    #     self.message_window.append("Plotting scans...")
    #     self.initial_view = self.grid.plot_points_initial()
    #     self.plot_widgets.addTab(self.initial_view.native, "Initial Plot")
    #     self.message_window.append(" ")

    # def click_run_alignment_button(self):
    #     print("Calculate the depth")
    #     self.message_window.append(" ")

    # def click_flag_vegetation_button(self):
    #     self.message_window.append("Creating grid and adding points.")
    #     self.grid.make_grid_by_cell()
    #     self.message_window.append("Complete!")
    #     self.message_window.append("Flagging cells...")
    #     count, num_cells = self.grid.flag_vegetation('snow')
    #     self.message_window.append(str(count) + " out of " + str(num_cells) + " cells with vegetation and/or cliffs.")
    #     self.message_window.append(" ")

    # def click_snow_depth_button(self):
    #     self.message_window.append("Calculating snow depth...")
    #     average, maximum, minimum = self.grid.calculate_snow_depth()
    #     self.message_window.append("Average Depth: " + str(average))
    #     self.message_window.append("Max Depth: " + str(maximum))
    #     self.message_window.append("Minimum Depth: " + str(minimum))
    #     self.message_window.append(" ")

    def click_plot_snowdepth_button(self):
        self.message_window.append("Coloring and plotting.... ")
        self.manager.check_flags()


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