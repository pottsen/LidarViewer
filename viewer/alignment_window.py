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
        # pointer to alignment manager
        self.manager = Manager(self, file_manager)

        # initialize interface
        self.initInterface()

        # sef flag defaults
        self.color_basis = 'default'
        self.alignment_basis = 'default'


    def initInterface(self):
        self.setWindowTitle("Lidar Snow Depth Calculator")
        
        # initialize left dock/side of window
        self.leftDock = QDockWidget('Data Options', self)
        self.leftDock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.leftDock.setAcceptDrops(False)
        self.left_dock()

        # initialze bottom dock/side of window
        self.bottomDock = QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        self.bottomDock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.bottom_dock()

        # initialize main panel
        self.main_panel()

    def files_update(self):
        self.left_dock()
        if len(self.manager.file_list) > 1:
            self.add_match_area_button.setEnabled(True)

    def left_dock(self):
        # initialize needed layouts
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
        Left algorithm widget. Contains actions for the window
        """
        # initialize layout
        self.alg_widget_layout = QVBoxLayout()

        # color selection for alignment plot
        self.color_checkbox_layout = QHBoxLayout()
        self.color_basis_label = QLabel('Color By:')
        self.color_default_checkbox = QCheckBox('Default')
        self.color_default_checkbox.stateChanged.connect(lambda:self.set_color_basis_default())
        self.color_default_checkbox.setEnabled(False)
        self.color_vegetation_checkbox = QCheckBox('Cliffs/Vegetation')
        self.color_vegetation_checkbox.stateChanged.connect(lambda:self.set_color_basis_vegetation())
        self.color_vegetation_checkbox.setEnabled(False)
        self.color_checkbox_layout.addWidget(self.color_basis_label)
        self.color_checkbox_layout.addWidget(self.color_default_checkbox)
        self.color_checkbox_layout.addWidget(self.color_vegetation_checkbox)
        self.color_checkbox_widget = QWidget()
        self.color_checkbox_widget.setLayout(self.color_checkbox_layout)
        self.alg_widget_layout.addWidget(self.color_checkbox_widget)

        # 'Add Match Area' Button --  Plots scans to select points for alignemnt or run on cliffs and trees as default
        self.add_match_area_button = QPushButton("Add Match Area")
        self.add_match_area_button.clicked.connect(self.click_add_match_area_button)
        self.add_match_area_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.add_match_area_button)

        # 'SelectPoints' Button -- Select points for alignment if desired
        self.select_points_button = QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.select_points_button)

        # 'Set Match Area' Button --  adds selected points to list of points to match on
        self.set_match_area_button = QPushButton("Set Match Area")
        self.set_match_area_button.clicked.connect(self.click_set_match_area_button)
        self.set_match_area_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.set_match_area_button)

        # alignment selection for alignment algorithm
        self.alignment_checkbox_layout = QHBoxLayout()
        self.alignment_basis_label = QLabel('Align By:')
        self.alignment_default_checkbox = QCheckBox('Cliffs/Veg')
        self.alignment_default_checkbox.stateChanged.connect(lambda:self.set_alignment_basis_default())
        self.alignment_default_checkbox.setEnabled(False)
        self.alignment_selection_checkbox = QCheckBox('Selection')
        self.alignment_selection_checkbox.stateChanged.connect(lambda:self.set_alignment_basis_selection())
        self.alignment_selection_checkbox.setEnabled(False)
        self.alignment_checkbox_layout.addWidget(self.alignment_basis_label)
        self.alignment_checkbox_layout.addWidget(self.alignment_default_checkbox)
        self.alignment_checkbox_layout.addWidget(self.alignment_selection_checkbox)

        self.alignment_checkbox_widget = QWidget()
        self.alignment_checkbox_widget.setLayout(self.alignment_checkbox_layout)
        self.alg_widget_layout.addWidget(self.alignment_checkbox_widget)

        # 'Run Alignemnt' Button -- runs alignemnt on the selected points
        self.run_alignment_button = QPushButton("Run Alignment")
        self.run_alignment_button.clicked.connect(self.click_run_alignment_button)
        self.run_alignment_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.run_alignment_button)

        # 'Set Alignment' Button -- accepts the determined alignment after running the match
        self.set_alignment_button = QPushButton("Set Alignment")
        self.set_alignment_button.clicked.connect(self.click_set_alignment_button)
        self.set_alignment_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.set_alignment_button)

        # 'Save Match' Button -- save newly aligned scan to a new file for later use
        self.save_match_button = QPushButton("Save Match")
        self.save_match_button.clicked.connect(self.click_save_match_button)
        self.save_match_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.save_match_button)

        # 'Reset/Clear' Button -- clear window and scans. Don't save any changes
        self.reset_button = QPushButton("Reset/Clear")
        self.reset_button.clicked.connect(self.click_reset_button)
        self.alg_widget_layout.addWidget(self.reset_button)
        
        # Add algorithms layout to widget
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

        self.plot_widgets.tabBar().setObjectName("mainTab")
        self.setCentralWidget(self.plot_widgets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDock)


    def click_load_file_button(self):
        # open built-in dialogue window to load scan
        file_path = QFileDialog.getOpenFileName()
        if 'las' in str(file_path[0]).lower():
            print(file_path)
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file_to_manager(str(file_path[0])) 
            self.message_window.append(" ")

    def set_color_basis_default(self):
        # sets plot color basis when 'default' checkbox selected or deselected
        if self.color_default_checkbox.isChecked():
            self.color_basis = 'default'
            self.color_vegetation_checkbox.setChecked(False)
            self.color_vegetation_checkbox.setEnabled(False)
            
        if not self.color_default_checkbox.isChecked():
            self.color_basis = 'default'
            self.color_vegetation_checkbox.setChecked(False)
            self.color_vegetation_checkbox.setEnabled(True)

    def set_color_basis_vegetation(self):
        # sets plot color basis when 'vegetation' checkbox selected or deselected
        if self.color_vegetation_checkbox.isChecked():
            self.color_basis = 'vegetation'
            self.color_default_checkbox.setChecked(False)
            self.color_default_checkbox.setEnabled(False)
            
        if not self.color_vegetation_checkbox.isChecked():
            self.color_basis = 'default'
            self.color_default_checkbox.setChecked(False)
            self.color_default_checkbox.setEnabled(True)

    def click_add_match_area_button(self):
        # check to make sure a 'Base' and 'Alignment' File are selected
        if self.manager.count_checked_files() != 2:
            self.message_window.append("Please select 2 files.")
            return
        
        # initialize/reset selected areas
        self.manager.scene_1_selected_areas = []
        self.manager.scene_2_selected_areas = []

        # add scenes
        self.manager.add_scene("Base")
        self.manager.add_scene("Alignment")

        # reset plot tabs and plot selected scans
        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.manager.scene_1, "Base")
        self.plot_widgets.addTab(self.manager.scene_2, "Alignment")
        
        # enable the appropriate button and checkboxes
        self.select_points_button.setEnabled(True)
        self.select_points_button.setChecked(False)
        self.alignment_default_checkbox.setEnabled(True)
        self.alignment_default_checkbox.setChecked(False)
        self.set_match_area_button.setEnabled(True)
        self.run_alignment_button.setEnabled(False)
        self.set_alignment_button.setEnabled(False)
        self.save_match_button.setEnabled(False)
        print("Base and Alignment file plotted.")


    def click_select_points_button(self):
        # enter select mode
        self.manager.select_points()

    def click_set_match_area_button(self):
        # add selected poiints to selected area list
        self.manager.set_match_area()
        print("s1 selected length", len(self.manager.scene_1_selected_areas))
        print("s2 selected length", len(self.manager.scene_2_selected_areas))
        self.alignment_selection_checkbox.setEnabled(True)
        self.run_alignment_button.setEnabled(True)

    def set_alignment_basis_default(self):
        # set alighnemnt basis to 'default' (cliffs/trees)
        if self.alignment_default_checkbox.isChecked():
            self.alignment_basis = 'default'
            self.alignment_selection_checkbox.setChecked(False)
            self.alignment_selection_checkbox.setEnabled(False)
            self.run_alignment_button.setEnabled(True)
            
        if not self.alignment_default_checkbox.isChecked():
            self.alignment_basis = 'default'
            self.alignment_selection_checkbox.setChecked(False)
            self.alignment_selection_checkbox.setEnabled(True)
            self.run_alignment_button.setEnabled(False)

    def set_alignment_basis_selection(self):
        # set alighnemnt basis to 'selection'
        if self.alignment_selection_checkbox.isChecked():
            self.alignment_basis = 'selection'
            self.alignment_default_checkbox.setChecked(False)
            self.alignment_default_checkbox.setEnabled(False)
            self.run_alignment_button.setEnabled(True)
            
        if not self.alignment_selection_checkbox.isChecked():
            self.alignment_basis = 'selection'
            self.alignment_default_checkbox.setChecked(False)
            self.alignment_default_checkbox.setEnabled(True)
            self.run_alignment_button.setEnabled(False)

    def click_run_alignment_button(self):
        # Check for the alignment basis
        if self.alignment_basis == 'selection':
            if self.manager.scene_1_selected_areas != [] and self.manager.scene_2_selected_areas != []:
                self.manager.scene_1_selected_areas = np.concatenate(self.manager.scene_1_selected_areas)
                print(self.manager.scene_1_selected_areas)
                self.manager.scene_2_selected_areas = np.concatenate(self.manager.scene_2_selected_areas)
                print(self.manager.scene_2_selected_areas)
                # self.manager.run_alignment()
                # self.set_alignment_button.setEnabled(True)
                # self.save_match_button.setEnabled(True)
            else:
                self.message_window.append('Please select points in both scans.')
                return

        # if self.alignment_basis == 'default':
        self.manager.run_alignment()
        self.set_alignment_button.setEnabled(True)
        self.save_match_button.setEnabled(True)

    def click_set_alignment_button(self):
        self.manager.set_alignment()

    def click_select_points_button(self):
        self.manager.select_points()

    def click_save_match_button(self):
        save_file_path, file_type = QFileDialog.getSaveFileName()
        if save_file_path != '':
            self.manager.save_matched_file(save_file_path)

    def click_reset_button(self):
        # reset everything in window
        self.manager.file_manager.reset_files()
        self.plot_widgets.clear()
        self.select_points_button.setChecked(False)
        self.select_points_button.setEnabled(False)
        self.set_match_area_button.setEnabled(False)
        self.alignment_default_checkbox.setEnabled(False)
        self.alignment_default_checkbox.setChecked(False)
        self.alignment_selection_checkbox.setEnabled(False)
        self.alignment_default_checkbox.setChecked(False)
        self.set_alignment_button.setEnabled(False)
        self.run_alignment_button.setEnabled(False)
        self.save_match_button.setEnabled(False)
        