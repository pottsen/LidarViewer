from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
import vispy.app
import sys
from grid import Grid
from depth_manager import Manager
import numpy as np

class Window(QtWidgets.QMainWindow):
    def __init__(self, file_manager):
        super(Window, self).__init__()
        # pointer to alignment manager
        self.manager = Manager(self, file_manager)

        # initialize interface
        self.initInterface()

        # sef flag defaults
        self.scan_basis = None
        self.color_basis = None


    def initInterface(self):
        # initialize left dock/side of window
        self.leftDock = QtWidgets.QDockWidget('Data Options', self)
        self.leftDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.leftDock.setAcceptDrops(False)
        self.left_dock()

        # initialze bottom dock/side of window
        self.bottomDock = QtWidgets.QDockWidget('Output', self)
        self.bottomDock.setAcceptDrops(False)
        self.bottomDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.bottom_dock()

        # initialize main panel
        self.main_panel()

    def files_update(self):
        # reload dock after loading file
        self.left_dock()
        if len(self.manager.file_list) > 0:
            self.vegetation_button.setEnabled(True)

    def left_dock(self):
        # initialize needed layouts
        self.left_dock_widget_layout = QtWidgets.QVBoxLayout()
        self.data_widget_layout = QtWidgets.QVBoxLayout()

        """
        Left data widget. Button to load in data and check boxes for files
        """
        # widget to contain file objects from manager
        self.plot_widget_layout = QtWidgets.QVBoxLayout()
        self.load_file_button = QtWidgets.QPushButton("Load Data")
        self.load_file_button.clicked.connect(self.click_load_file_button)
        self.data_widget_layout.addWidget(self.load_file_button)

        self.file_box = QtWidgets.QWidget()
        self.file_layout = QtWidgets.QVBoxLayout()
        
        for i in range(len(self.manager.file_list)):
            self.file_layout.addWidget(self.manager.file_list[i])
        
        self.file_box.setLayout(self.file_layout)
        self.data_widget_layout.addWidget(self.file_box)

        self.data_widget = QtWidgets.QWidget()
        self.data_widget.setLayout(self.data_widget_layout)
        self.left_dock_widget_layout.addWidget(self.data_widget)

        """
        Left algorithm widget. Buttons to flag vegetation and calculate snowdepth
        """
        # initialize layout
        self.alg_widget_layout = QtWidgets.QVBoxLayout()

        # find vegetation button
        self.vegetation_button = QtWidgets.QPushButton("Find Vegetation and Cliffs")
        self.vegetation_button.clicked.connect(self.click_vegetation_button)
        self.vegetation_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.vegetation_button)

        # calculate snow depth button
        self.calculate_snowdepth_button = QtWidgets.QPushButton("Calculate Snow Depth")
        self.calculate_snowdepth_button.clicked.connect(self.click_snowdepth_button)
        self.calculate_snowdepth_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.calculate_snowdepth_button)

        self.alg_widget = QtWidgets.QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Left plot widget. Has all the plotting options in it.
        """
        # color basis selection for plot
        self.color_checkbox_layout = QtWidgets.QHBoxLayout()
        self.color_basis_label = QtWidgets.QLabel('Color By:')
        self.intensity_basis_checkbox = QCheckBox('Intensity')
        self.intensity_basis_checkbox.stateChanged.connect(lambda:self.set_color_basis_intensity())
        self.intensity_basis_checkbox.setEnabled(False)
        self.snowdepth_basis_checkbox = QCheckBox('Snow Depth')
        self.snowdepth_basis_checkbox.stateChanged.connect(lambda:self.set_color_basis_snowdepth())
        self.snowdepth_basis_checkbox.setEnabled(False)
        self.color_checkbox_layout.addWidget(self.color_basis_label)
        self.color_checkbox_layout.addWidget(self.intensity_basis_checkbox)
        self.color_checkbox_layout.addWidget(self.snowdepth_basis_checkbox)
        self.color_checkbox_widget = QtWidgets.QWidget()
        self.color_checkbox_widget.setLayout(self.color_checkbox_layout)
        self.plot_widget_layout.addWidget(self.color_checkbox_widget)

        # scan basis selection for plot
        self.basis_checkbox_layout = QtWidgets.QHBoxLayout()
        self.basis_label = QtWidgets.QLabel('Basis:')
        self.ground_basis_checkbox = QCheckBox('Ground')
        self.ground_basis_checkbox.stateChanged.connect(lambda:self.set_ground_basis())
        self.ground_basis_checkbox.setEnabled(False)
        self.intSnow_basis_checkbox = QCheckBox('Int. Snow')
        self.intSnow_basis_checkbox.stateChanged.connect(lambda:self.set_intSnow_basis())
        self.intSnow_basis_checkbox.setEnabled(False)
        self.new_snow_basis_checkbox = QCheckBox('New Snow')
        self.new_snow_basis_checkbox.stateChanged.connect(lambda:self.set_new_snow_basis())
        self.new_snow_basis_checkbox.setEnabled(False)
        self.basis_checkbox_layout.addWidget(self.basis_label)
        self.basis_checkbox_layout.addWidget(self.ground_basis_checkbox)
        self.basis_checkbox_layout.addWidget(self.intSnow_basis_checkbox)
        self.basis_checkbox_layout.addWidget(self.new_snow_basis_checkbox)
        self.basis_checkbox_widget = QtWidgets.QWidget()
        self.basis_checkbox_widget.setLayout(self.basis_checkbox_layout)
        self.plot_widget_layout.addWidget(self.basis_checkbox_widget)
        
        # Upper/Lower and Maximum/Minimum bound input and display widgets
        self.max_label_layout = QtWidgets.QHBoxLayout()
        self.max_label_name = QtWidgets.QLabel('Max:')
        self.max_label_value = QtWidgets.QLabel('-')
        self.max_label_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.max_label_layout.addWidget(self.max_label_name)
        self.max_label_layout.addWidget(self.max_label_value)
        self.max_label_widget = QtWidgets.QWidget()
        self.max_label_widget.setLayout(self.max_label_layout)

        self.upperbound_label_layout = QtWidgets.QHBoxLayout()
        self.upperbound_label_name = QtWidgets.QLabel('Upper Bound:')
        self.upperbound_text_slot = QLineEdit()
        self.upperbound_text_slot.setEnabled(False)
        self.upperbound_label_layout.addWidget(self.upperbound_label_name)
        self.upperbound_label_layout.addWidget(self.upperbound_text_slot)
        self.upperbound_label_widget = QtWidgets.QWidget()
        self.upperbound_label_widget.setLayout(self.upperbound_label_layout)

        self.lowerbound_label_layout = QtWidgets.QHBoxLayout()
        self.lowerbound_label_name = QtWidgets.QLabel('Lower Bound:')
        self.lowerbound_text_slot = QLineEdit()
        self.lowerbound_text_slot.setEnabled(False)
        self.lowerbound_label_layout.addWidget(self.lowerbound_label_name)
        self.lowerbound_label_layout.addWidget(self.lowerbound_text_slot)

        self.lowerbound_label_widget = QtWidgets.QWidget()
        self.lowerbound_label_widget.setLayout(self.lowerbound_label_layout)

        self.min_label_layout = QtWidgets.QHBoxLayout()
        self.min_label_name = QtWidgets.QLabel('Min:')
        self.min_label_value = QtWidgets.QLabel('-')
        self.min_label_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min_label_layout.addWidget(self.min_label_name)
        self.min_label_layout.addWidget(self.min_label_value)

        self.min_label_widget = QtWidgets.QWidget()
        self.min_label_widget.setLayout(self.min_label_layout)

        self.plot_widget_layout.addWidget(self.max_label_widget)
        self.plot_widget_layout.addWidget(self.upperbound_label_widget)
        self.plot_widget_layout.addWidget(self.lowerbound_label_widget)
        self.plot_widget_layout.addWidget(self.min_label_widget)


        # Plot widget button
        self.plot_button = QtWidgets.QPushButton("Plot")
        self.plot_button.clicked.connect(self.click_plot_button)
        self.plot_button.setEnabled(False)
        self.plot_widget_layout.addWidget(self.plot_button)

        self.plot_widget = QtWidgets.QWidget()
        self.plot_widget.setLayout(self.plot_widget_layout)
        self.left_dock_widget_layout.addWidget(self.plot_widget)

        # Select points button
        self.stats_widget_layout = QtWidgets.QVBoxLayout()
        self.select_points_button = QtWidgets.QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        self.stats_widget_layout.addWidget(self.select_points_button)
        self.stats_widget = QtWidgets.QWidget()
        self.stats_widget.setLayout(self.stats_widget_layout)
        self.left_dock_widget_layout.addWidget(self.stats_widget)

        """
        Make left dock widget.
        """
        self.left_dock_widget = QtWidgets.QWidget()
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
        # self.plot_widgets = QtWidgets.QWidget()

        self.plot_widgets.tabBar().setObjectName("mainTab")
        self.setCentralWidget(self.plot_widgets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDock)

    def set_color_basis_intensity(self):
        # enable/disable check boxes for intensity color basis
        if self.intensity_basis_checkbox.isChecked():
            self.color_basis = 'intensity'
            self.snowdepth_basis_checkbox.setChecked(False)
            self.snowdepth_basis_checkbox.setEnabled(False)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(True)

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(True)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(True)

        # enable/disable check boxes for intensity color basis    
        if not self.intensity_basis_checkbox.isChecked():
            self.color_basis = 'intensity'
            self.snowdepth_basis_checkbox.setChecked(False)
            self.snowdepth_basis_checkbox.setEnabled(True)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(False)

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(False)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(False)

    def set_color_basis_snowdepth(self):
        # enable/disable check boxes for depth color basis
        if self.snowdepth_basis_checkbox.isChecked():
            self.color_basis = 'depth'
            self.intensity_basis_checkbox.setChecked(False)
            self.intensity_basis_checkbox.setEnabled(False)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(True)

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(True)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(False)

        # enable/disable check boxes for intensity color basis    
        if not self.snowdepth_basis_checkbox.isChecked():
            self.color_basis = None
            self.intensity_basis_checkbox.setChecked(False)
            self.intensity_basis_checkbox.setEnabled(True)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(False)

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(False)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(False)

        
    def set_ground_basis(self):
        # enable/disable check boxes for depth color basis
        if self.ground_basis_checkbox.isChecked():
            self.scan_basis = 'Ground'

            max_bound, min_bound = self.manager.get_basis_info(self.color_basis, self.scan_basis)

            if max_bound == '-':
                self.scan_basis = None
                self.ground_basis_checkbox.setChecked(False)
                self.ground_basis_checkbox.setCheckState(False)
                return

            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(True)
            self.lowerbound_text_slot.setEnabled(True)


            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(False)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(False)

        # enable/disable check boxes for depth color basis
        if not self.ground_basis_checkbox.isChecked():
            self.scan_basis = None

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(True)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(True)

            max_bound, min_bound = self.manager.reset_basis_info()
            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(False)
            self.lowerbound_text_slot.setEnabled(False)

    def set_intSnow_basis(self):
        # enable/disable check boxes for depth color basis
        if self.intSnow_basis_checkbox.isChecked():
            self.scan_basis = 'Int. Snow'

            max_bound, min_bound = self.manager.get_basis_info(self.color_basis, self.scan_basis)

            if max_bound == '-':
                print('max bound', max_bound)
                self.scan_basis = None
                self.intSnow_basis_checkbox.setChecked(False)
                self.intSnow_basis_checkbox.setCheckState(False)
                return
            
            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(True)
            self.lowerbound_text_slot.setEnabled(True)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(False)

            self.new_snow_basis_checkbox.setChecked(False)
            self.new_snow_basis_checkbox.setEnabled(False)

            
        # enable/disable check boxes for depth color basis
        if not self.intSnow_basis_checkbox.isChecked():
            self.scan_basis = None
            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(True)

            if self.color_basis != 'depth':
                self.new_snow_basis_checkbox.setChecked(False)
                self.new_snow_basis_checkbox.setEnabled(True)
            max_bound, min_bound = self.manager.reset_basis_info()
            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(False)
            self.lowerbound_text_slot.setEnabled(False)

    def set_new_snow_basis(self):
        # enable/disable check boxes for depth color basis
        if self.new_snow_basis_checkbox.isChecked():
            self.scan_basis = 'New Snow'

            max_bound, min_bound = self.manager.get_basis_info(self.color_basis, self.scan_basis)

            if max_bound == '-':
                self.scan_basis = None
                self.new_snow_basis_checkbox.setChecked(False)
                self.new_snow_basis_checkbox.setCheckState(False)
                return

            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(True)
            self.lowerbound_text_slot.setEnabled(True)

            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(False)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(False)

        # enable/disable check boxes for depth color basis
        if not self.new_snow_basis_checkbox.isChecked():
            self.scan_basis = None
            self.intSnow_basis_checkbox.setChecked(False)
            self.intSnow_basis_checkbox.setEnabled(True)

            self.ground_basis_checkbox.setChecked(False)
            self.ground_basis_checkbox.setEnabled(True)
            max_bound, min_bound = self.manager.reset_basis_info()
            self.max_label_value.setText(str(max_bound))
            self.min_label_value.setText(str(min_bound))
            self.upperbound_text_slot.setEnabled(False)
            self.lowerbound_text_slot.setEnabled(False)

    def click_load_file_button(self):
        # open built-in dialogue window to load scan 
        file_path = QFileDialog.getOpenFileName()
        if 'las' in str(file_path[0]).lower():
            print(file_path)
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file_to_manager(str(file_path[0])) 
            self.message_window.append(" ")

        if len(self.manager.file_list) > 0:
            self.vegetation_button.setEnabled(True)

    def click_vegetation_button(self):
        # button action to run the vegetation algorithm
        self.intensity_basis_checkbox.setCheckState(False)
        self.intensity_basis_checkbox.setEnabled(True)

        self.snowdepth_basis_checkbox.setCheckState(False)
        self.snowdepth_basis_checkbox.setEnabled(False)

        self.ground_basis_checkbox.setCheckState(False)
        self.ground_basis_checkbox.setEnabled(False)

        self.intSnow_basis_checkbox.setCheckState(False)
        self.intSnow_basis_checkbox.setEnabled(False)

        self.new_snow_basis_checkbox.setCheckState(False)
        self.new_snow_basis_checkbox.setEnabled(False) 

        flag = self.manager.make_grid()  
        self.calculate_snowdepth_button.setEnabled(flag)
        self.plot_button.setEnabled(flag)     

    def click_snowdepth_button(self):
        # button action to run the snow depth algorithm
        self.manager.calculate_snow_depth()
        self.intensity_basis_checkbox.setEnabled(True)
        self.snowdepth_basis_checkbox.setEnabled(True)
        max_bound, min_bound = self.manager.reset_basis_info()
        self.max_label_value.setText(str(max_bound))
        self.min_label_value.setText(str(min_bound))


    def click_plot_button(self):
        # button action to plot the scans
        if self.upperbound_text_slot.text() != '':
            upper_bound = int(self.upperbound_text_slot.text())
        else:
            upper_bound = ''
        if self.lowerbound_text_slot.text() != '':
            lower_bound = int(self.lowerbound_text_slot.text())
        else:
            lower_bound = ''
        
        if upper_bound < lower_bound:
            self.message_window.append("Warning: Upper Bound is less than lower bound")
            return

        scene, upper_bound, lower_bound = self.manager.color_and_plot_points(self.color_basis, self.scan_basis, upper_bound, lower_bound)
        self.plot_widgets.clear()
        self.plot_widgets.addTab(scene, "Plot")
        if self.color_basis == 'intensity':
            if self.upperbound_text_slot.text == '':
                self.upperbound_text_slot.setText(str(upper_bound))
            if self.lowerbound_text_slot.text == '':
                self.lowerbound_text_slot.setText(str(lower_bound))
        self.select_points_button.setEnabled(True)
        self.select_points_button.setChecked(False)

    def click_select_points_button(self):
        # enter select mode
        self.manager.select_points()