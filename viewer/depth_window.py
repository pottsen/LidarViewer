from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from depth_manager import Manager
import numpy as np
# from scene import DemoScene

class Window(QtWidgets.QMainWindow):
    # resize = pyqtSignal()
    def __init__(self, file_manager):
        super(Window, self).__init__()
        # self.setWindowTitle("Lidar Snow Depth Calculator")
        self.manager = Manager(self, file_manager)
        self.initInterface()
        self.scan_basis = None
        self.color_basis = None


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
        if len(self.manager.file_list) > 0:
            self.vegetation_button.setEnabled(True)

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
        self.vegetation_button.setEnabled(False)
        self.calculate_snowdepth_button = QPushButton("Calculate Snow Depth")
        self.calculate_snowdepth_button.clicked.connect(self.click_snowdepth_button)
        self.calculate_snowdepth_button.setEnabled(False)

        self.alg_widget_layout.addWidget(self.vegetation_button)
        self.alg_widget_layout.addWidget(self.calculate_snowdepth_button)

        self.alg_widget = QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Left plot widget. Has all the plotting options in it.
        """
        
        self.color_checkbox_layout = QHBoxLayout()
        self.color_basis_label = QLabel('Color By:')
        self.intensity_basis_checkbox = QCheckBox('Intensity')
        self.intensity_basis_checkbox.stateChanged.connect(lambda:self.set_color_basis_intensity())
        self.intensity_basis_checkbox.setEnabled(False)
        self.snowdepth_basis_checkbox = QCheckBox('Snow Depth')
        self.snowdepth_basis_checkbox.stateChanged.connect(lambda:self.set_color_basis_snowdepth())
        self.snowdepth_basis_checkbox.setEnabled(False)
        self.color_checkbox_layout.addWidget(self.color_basis_label)
        self.color_checkbox_layout.addWidget(self.intensity_basis_checkbox)
        self.color_checkbox_layout.addWidget(self.snowdepth_basis_checkbox)

        self.color_checkbox_widget = QWidget()
        self.color_checkbox_widget.setLayout(self.color_checkbox_layout)
        self.plot_widget_layout.addWidget(self.color_checkbox_widget)

        self.basis_checkbox_layout = QHBoxLayout()
        self.basis_label = QLabel('Basis:')
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

        self.basis_checkbox_widget = QWidget()
        self.basis_checkbox_widget.setLayout(self.basis_checkbox_layout)
        self.plot_widget_layout.addWidget(self.basis_checkbox_widget)
        
        
        # self.depth_checkbox_layout = QHBoxLayout()
        # self.depth_basis_label = QLabel('Depth Basis:')
        # self.ground_basis_checkbox = QCheckBox('Ground')
        # self.ground_basis_checkbox.stateChanged.connect(lambda:self.get_ground_basis_info())
        # self.ground_basis_checkbox.setEnabled(False)
        # self.intSnow_basis_checkbox = QCheckBox('Int. Snow')
        # self.intSnow_basis_checkbox.stateChanged.connect(lambda:self.get_intSnow_basis_info())
        # self.intSnow_basis_checkbox.setEnabled(False)
        # self.depth_checkbox_layout.addWidget(self.depth_basis_label)
        # self.depth_checkbox_layout.addWidget(self.ground_basis_checkbox)
        # self.depth_checkbox_layout.addWidget(self.intSnow_basis_checkbox)

        # self.depth_checkbox_widget = QWidget()
        # self.depth_checkbox_widget.setLayout(self.depth_checkbox_layout)
        # self.plot_widget_layout.addWidget(self.depth_checkbox_widget)


        self.max_label_layout = QHBoxLayout()
        self.max_label_name = QLabel('Max:')
        self.max_label_value = QLabel('-')
        self.max_label_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.max_label_layout.addWidget(self.max_label_name)
        self.max_label_layout.addWidget(self.max_label_value)

        self.max_label_widget = QWidget()
        self.max_label_widget.setLayout(self.max_label_layout)

        self.upperbound_label_layout = QHBoxLayout()
        self.upperbound_label_name = QLabel('Upper Bound:')
        self.upperbound_text_slot = QLineEdit()
        self.upperbound_text_slot.setEnabled(False)
        self.upperbound_label_layout.addWidget(self.upperbound_label_name)
        self.upperbound_label_layout.addWidget(self.upperbound_text_slot)

        self.upperbound_label_widget = QWidget()
        self.upperbound_label_widget.setLayout(self.upperbound_label_layout)

        self.lowerbound_label_layout = QHBoxLayout()
        self.lowerbound_label_name = QLabel('Lower Bound:')
        self.lowerbound_text_slot = QLineEdit()
        self.lowerbound_text_slot.setEnabled(False)
        self.lowerbound_label_layout.addWidget(self.lowerbound_label_name)
        self.lowerbound_label_layout.addWidget(self.lowerbound_text_slot)

        self.lowerbound_label_widget = QWidget()
        self.lowerbound_label_widget.setLayout(self.lowerbound_label_layout)

        self.min_label_layout = QHBoxLayout()
        self.min_label_name = QLabel('Min:')
        self.min_label_value = QLabel('-')
        self.min_label_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min_label_layout.addWidget(self.min_label_name)
        self.min_label_layout.addWidget(self.min_label_value)

        self.min_label_widget = QWidget()
        self.min_label_widget.setLayout(self.min_label_layout)

        self.plot_widget_layout.addWidget(self.max_label_widget)
        self.plot_widget_layout.addWidget(self.upperbound_label_widget)
        self.plot_widget_layout.addWidget(self.lowerbound_label_widget)
        self.plot_widget_layout.addWidget(self.min_label_widget)
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.click_plot_button)
        self.plot_button.setEnabled(False)
        self.plot_widget_layout.addWidget(self.plot_button)

        self.plot_widget = QWidget()
        self.plot_widget.setLayout(self.plot_widget_layout)
        self.left_dock_widget_layout.addWidget(self.plot_widget)

        self.stats_widget_layout = QVBoxLayout()
        self.select_points_button = QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        self.stats_widget_layout.addWidget(self.select_points_button)
        self.stats_widget = QWidget()
        self.stats_widget.setLayout(self.stats_widget_layout)
        self.left_dock_widget_layout.addWidget(self.stats_widget)

    

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

    def set_color_basis_intensity(self):
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
            # max_bound, min_bound = self.manager.get_intensity_basis_info()
            # self.max_label_value.setText(str(max_bound))
            # self.min_label_value.setText(str(min_bound))
            
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
            # max_bound, min_bound = self.manager.get_intensity_basis_info()
            # self.max_label_value.setText(str(max_bound))
            # self.min_label_value.setText(str(min_bound))
            
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
        file_path = QFileDialog.getOpenFileName()
        print(file_path)
        if 'las' in str(file_path[0]).lower():
            self.message_window.append("Cleaning and loading file: " + str(file_path[0]))
            self.manager.add_file_to_manager(str(file_path[0])) 
            self.message_window.append(" ")

        if len(self.manager.file_list) > 0:
            self.vegetation_button.setEnabled(True)

    def click_vegetation_button(self):
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
        self.manager.calculate_snow_depth()
        self.intensity_basis_checkbox.setEnabled(True)
        self.snowdepth_basis_checkbox.setEnabled(True)
        max_bound, min_bound = self.manager.reset_basis_info()
        self.max_label_value.setText(str(max_bound))
        self.min_label_value.setText(str(min_bound))


    def click_plot_button(self):
        # if self.ground_basis_checkbox.isEnabled():
        if self.upperbound_text_slot.text() != '':
            upper_bound = int(self.upperbound_text_slot.text())
        else:
            upper_bound = ''
        if self.lowerbound_text_slot.text() != '':
            lower_bound = int(self.lowerbound_text_slot.text())
        else:
            lower_bound = ''
        
        self.scene = self.manager.color_and_plot_points(self.color_basis, self.scan_basis, upper_bound, lower_bound)
        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.scene, "Plot")
        # self.select_points_button.setEnabled(False)
        self.select_points_button.setEnabled(True)
        self.select_points_button.setChecked(False)

    def click_select_points_button(self):
        self.manager.select_points()