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
        self.manager = Manager(self)
        self.initInterface()


    def initInterface(self):
        self.setWindowTitle("Lidar Snow Depth Calculator")
        
        self.leftDock = QDockWidget('Data Options', self)
        self.leftDock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        self.leftDock.setAcceptDrops(False)
        self.left_dock()

        self.bottomDock = QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        self.bottomDock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
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
        self.vegetation_button.clicked.connect(self.click_vegetation_button)
        self.calculate_snowdepth_button = QPushButton("Calculate Snow Depth")
        self.calculate_snowdepth_button.clicked.connect(self.click_snowdepth_button)

        self.alg_widget_layout.addWidget(self.vegetation_button)
        self.alg_widget_layout.addWidget(self.calculate_snowdepth_button)

        self.alg_widget = QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Left plot widget. Has all the plotting options in it.
        """
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.click_plot_button)
        self.plot_widget_layout.addWidget(self.plot_button)

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
        print(file_path)
        if 'las' in str(file_path[0]).lower():
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file(str(file_path[0])) 
            self.message_window.append(" ")
            self.manager.clear_flags()
            self.left_dock()


    # def click_plot_initial_button(self):
    #     self.message_window.append("Plotting scans...")
    #     self.initial_view = self.grid.plot_points_initial()
    #     self.plot_widgets.addTab(self.initial_view.native, "Initial Plot")
    #     self.message_window.append(" ")

    # def click_run_alignment_button(self):
    #     print("Calculate the depth")
    #     self.message_window.append(" ")

    def click_vegetation_button(self):
        self.manager.make_grid()
        self.manager.flag_vegetation()

    def click_snowdepth_button(self):
        self.manager.calculate_snow_depth()


    def click_plot_button(self):
        self.manager.color_points('Ground')
        self.view = self.manager.plot_points()
        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.view.native, "Plot")


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