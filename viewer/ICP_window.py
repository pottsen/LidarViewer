from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
from canvas import Canvas
import vispy.app
import sys
from grid import Grid
from ICP_manager import Manager, file_object
import numpy as np
import ICP_algorithm as ia
# from scene import DemoScene

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.manager = Manager(self)
        self.initInterface()
        self.scene_1 = None
        self.scene_2 = None
        self.scene_1_selected_areas = []
        self.scene_2_selected_areas = []


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
        self.plot_initial_button = QPushButton("Plot Initial")
        self.plot_initial_button.clicked.connect(self.click_plot_initial_button)
        self.plot_initial_button.setEnabled(False)
        self.add_match_area_button = QPushButton("Add Match Area")
        self.add_match_area_button.clicked.connect(self.click_add_match_area_button)
        self.add_match_area_button.setEnabled(False)
        self.select_points_button = QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        # self.scan_1_button = QPushButton("Scan 1")
        # self.scan_1_button.clicked.connect(self.click_scan_1_button)
        # self.scan_1_button.setEnabled(False)
        # self.scan_2_button = QPushButton("Scan 2")
        # self.scan_2_button.clicked.connect(self.click_scan_2_button)
        # self.scan_2_button.setEnabled(False)
        self.set_match_area_button = QPushButton("Set Match Area")
        self.set_match_area_button.clicked.connect(self.click_set_match_area_button)
        self.set_match_area_button.setEnabled(False)
        self.run_alignment_button = QPushButton("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)
        self.run_alignment_button.setEnabled(False)

        self.alg_widget_layout.addWidget(self.plot_initial_button)
        self.alg_widget_layout.addWidget(self.add_match_area_button)
        self.alg_widget_layout.addWidget(self.select_points_button)
        # self.alg_widget_layout.addWidget(self.scan_1_button)
        # self.alg_widget_layout.addWidget(self.scan_2_button)
        self.alg_widget_layout.addWidget(self.set_match_area_button)
        self.alg_widget_layout.addWidget(self.run_alignment_button)

        self.alg_widget = QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Left plot widget. Has all the plotting options in it.
        """
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.click_plot_button)
        self.plot_button.setEnabled(False)
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
        # self.plot_widgets = QWidget()

        self.plot_widgets.tabBar().setObjectName("mainTab")
        self.setCentralWidget(self.plot_widgets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDock)

        # self.scene = DemoScene(keys='interactive')
        # self.plot_widgets.clear()
        # self.plot_widgets.addTab(self.scene, "Plot")

    def click_load_file_button(self):
        file_path = get_file()
        print(file_path)
        if 'las' in str(file_path[0]).lower():
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file(str(file_path[0])) 
            self.message_window.append(" ")
            self.manager.clear_flags()
            self.left_dock()
        if len(self.manager.file_list) > 0:
            self.plot_initial_button.setEnabled(True)
        if len(self.manager.file_list) > 1:
            self.add_match_area_button.setEnabled(True)


    def click_plot_initial_button(self):
        self.message_window.append("Plotting scans...")
        self.initial_view = self.grid.plot_points_initial()
        self.plot_widgets.addTab(self.initial_view.native, "Initial Plot")
        self.message_window.append(" ")

    def click_add_match_area_button(self):
        self.scene_1_selected_areas = []
        self.scene_2_selected_areas = []
        # set scan 1 scene
        # if self.scene_1 == None:
        self.scene_1 = self.manager.add_scene("Base")

        # set scan 2 scene
        # if self.scene_2 == None:
        self.scene_2 = self.manager.add_scene("Alignment")

        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.scene_1, "Scan 1")
        self.plot_widgets.addTab(self.scene_2, "Scan 2")
        
        self.select_points_button.setEnabled(True)
        self.set_match_area_button.setEnabled(True)
        print("Base and Alignment file plotted.")
        # self.scan_1_button.setEnabled(True)
        # self.scan_2_button.setEnabled(True)

    def click_select_points_button(self):
        self.manager.select_points()

    # def click_scan_1_button(self):
    #     self.plot_widgets.clear()
    #     self.plot_widgets.addTab(self.scene_1, "Scan 1")
    #     print("Scan 1 ready to view")

    # def click_scan_2_button(self):
    #     # self.plot_widgets.clear()
    #     self.plot_widgets.addTab(self.scene_2, "Scan 2")
    #     self.set_match_area_button.setEnabled(True)
    #     print("Scan 2 ready to view")

    def click_set_match_area_button(self):
        self.manager.set_match_area()
        print("s1 selected length", len(self.scene_1_selected_areas))
        print("s2 selected length", len(self.scene_2_selected_areas))
        self.run_alignment_button.setEnabled(True)
    

    def click_run_alignment_button(self):
        self.scene_1_selected_areas = np.concatenate(self.scene_1_selected_areas)
        print(self.scene_1_selected_areas)
        self.scene_2_selected_areas = np.concatenate(self.scene_2_selected_areas)
        print(self.scene_2_selected_areas)
        self.manager.run_alignment()


    def click_plot_button(self):
        self.manager.color_points(self.upperbound_text_slot.text(), self.lowerbound_text_slot.text())
        self.scene = self.manager.plot_points()
        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.scene, "Plot")
        self.select_points_button.setEnabled(True)

    def click_select_points_button(self):
        self.manager.select_points()