from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from alignment_manager import Manager, file_object
import numpy as np
import ICP_algorithm as ia
# from scene import DemoScene

class Window(QMainWindow):
    # resize = pyqtSignal()
    def __init__(self, file_manager):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.manager = Manager(self, file_manager)
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

    def files_update(self):
        self.left_dock()
        if len(self.manager.file_list) > 1:
            self.add_match_area_button.setEnabled(True)

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
        # self.plot_initial_button = QPushButton("Plot Initial")
        # self.plot_initial_button.clicked.connect(self.click_plot_initial_button)
        # self.plot_initial_button.setEnabled(False)
        self.add_match_area_button = QPushButton("Add Match Area")
        self.add_match_area_button.clicked.connect(self.click_add_match_area_button)
        self.add_match_area_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.add_match_area_button)

        self.select_points_button = QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.select_points_button)

        self.set_match_area_button = QPushButton("Set Match Area")
        self.set_match_area_button.clicked.connect(self.click_set_match_area_button)
        self.set_match_area_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.set_match_area_button)

        self.run_alignment_button = QPushButton("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)
        self.run_alignment_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.run_alignment_button)

        self.set_alignment_button = QPushButton("Set Alignment")
        self.set_alignment_button.clicked.connect(self.click_set_alignment_button)
        self.set_alignment_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.set_alignment_button)

        self.save_match_button = QPushButton("Save Match")
        self.save_match_button.clicked.connect(self.click_save_match_button)
        self.save_match_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.save_match_button)

        self.reset_button = QPushButton("Reset/Clear")
        self.reset_button.clicked.connect(self.click_reset_button)
        # self.reset_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.reset_button)
        
        self.alg_widget = QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

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
        file_path = QFileDialog.getOpenFileName()
        print(file_path)
        if 'las' in str(file_path[0]).lower():
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file_to_manager(str(file_path[0])) 
            self.message_window.append(" ")

    def click_add_match_area_button(self):
        if self.manager.count_checked_files() != 2:
            self.message_window.append("Please select 2 files.")
            return
        self.scene_1_selected_areas = []
        self.scene_2_selected_areas = []
        # set scan 1 scene
        # if self.scene_1 == None:
        self.scene_1 = self.manager.add_scene("Base")

        # set scan 2 scene
        # if self.scene_2 == None:
        self.scene_2 = self.manager.add_scene("Alignment")

        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.scene_1, "Base")
        self.plot_widgets.addTab(self.scene_2, "Alignment")
        
        self.select_points_button.setEnabled(True)
        self.select_points_button.setChecked(False)
        self.set_match_area_button.setEnabled(True)
        self.run_alignment_button.setEnabled(False)
        self.set_alignment_button.setEnabled(False)
        self.save_match_button.setEnabled(False)
        print("Base and Alignment file plotted.")


    def click_select_points_button(self):
        self.manager.select_points()

    def click_set_match_area_button(self):
        self.manager.set_match_area()
        print("s1 selected length", len(self.scene_1_selected_areas))
        print("s2 selected length", len(self.scene_2_selected_areas))
        self.run_alignment_button.setEnabled(True)

    def click_run_alignment_button(self):
        if self.scene_1_selected_areas != [] and self.scene_2_selected_areas != []:
            self.scene_1_selected_areas = np.concatenate(self.scene_1_selected_areas)
            print(self.scene_1_selected_areas)
            self.scene_2_selected_areas = np.concatenate(self.scene_2_selected_areas)
            print(self.scene_2_selected_areas)
            self.manager.run_alignment()
            self.set_alignment_button.setEnabled(True)
            self.save_match_button.setEnabled(True)
        else:
            self.message_window.append('Please select points in both scans.')

    def click_set_alignment_button(self):
        self.manager.set_alignment()

    def click_select_points_button(self):
        self.manager.select_points()

    def click_save_match_button(self):
        self.manager.save_matched_file()

    def click_reset_button(self):
        self.manager.file_manager.reset_files()
        self.plot_widgets.clear()
        self.select_points_button.setChecked(False)
        self.select_points_button.setEnabled(False)
        self.set_match_area_button.setEnabled(False)
        self.set_alignment_button.setEnabled(False)
        self.run_alignment_button.setEnabled(False)
        self.save_match_button.setEnabled(False)