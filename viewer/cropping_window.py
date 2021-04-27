from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
import vispy.app
import sys
from cropping_manager import Manager, crop_file_object
import numpy as np

class Window(QtWidgets.QMainWindow):
    def __init__(self, file_manager):
        super(Window, self).__init__()
        # pointer to crop manager
        self.manager = Manager(self, file_manager)
        
        # initialize interface
        self.initInterface()


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
        self.left_dock()
        if len(self.manager.file_list) > 0:
            self.plot_scan_button.setEnabled(True)

    def left_dock(self):
        # initialize needed layouts
        self.left_dock_widget_layout = QtWidgets.QVBoxLayout()
        self.data_widget_layout = QtWidgets.QVBoxLayout()

        """
        Left data widget. Button to load in data and check boxes for files
        """
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
        Left algorithm widget. Contains actions for the window
        """
        # initialize layout
        self.alg_widget_layout = QtWidgets.QVBoxLayout()

        # Plot Scans button
        self.plot_scan_button = QtWidgets.QPushButton("Plot Scans")
        self.plot_scan_button.clicked.connect(self.click_plot_scan_button)
        self.plot_scan_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.plot_scan_button)

        # Select Points button
        self.select_points_button = QtWidgets.QPushButton("Select Points")
        self.select_points_button.setCheckable(True)
        self.select_points_button.clicked.connect(self.click_select_points_button)
        self.select_points_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.select_points_button)

        # Remove Selected points button
        self.remove_selected_points_button = QtWidgets.QPushButton("Remove Selected")
        self.remove_selected_points_button.clicked.connect(self.click_remove_selected_points_button)
        self.remove_selected_points_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.remove_selected_points_button)

        # Save Crop 1 Scan button - Save 'Crop 1' Scan as a new file
        self.save_crop_1_button = QtWidgets.QPushButton("Save Cropped Scan 1")
        self.save_crop_1_button.clicked.connect(self.click_save_crop_1_button)
        self.save_crop_1_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.save_crop_1_button)

        # Save Crop 2 Scan button - Save 'Crop 2' Scan as a new file
        self.save_crop_2_button = QtWidgets.QPushButton("Save Cropped Scan 2")
        self.save_crop_2_button.clicked.connect(self.click_save_crop_2_button)
        self.save_crop_2_button.setEnabled(False)
        self.alg_widget_layout.addWidget(self.save_crop_2_button)

        # 'Reset/Clear' Button -- clear window and scans. Don't save any changes
        self.reset_button = QtWidgets.QPushButton("Reset/Clear")
        self.reset_button.clicked.connect(self.click_reset_button)
        self.alg_widget_layout.addWidget(self.reset_button)
        
        self.alg_widget = QtWidgets.QWidget()
        self.alg_widget.setLayout(self.alg_widget_layout)
        self.left_dock_widget_layout.addWidget(self.alg_widget)

        """
        Make left dock widget.
        """
        self.left_dock_widget = QtWidgets.QWidget()
        self.left_dock_widget.setLayout(self.left_dock_widget_layout)
        self.leftDock.setWidget(self.left_dock_widget)
        
    def bottom_dock(self):
        ##### BOTTOM TEXT DOCK AND WIDGET
        self.message_window = QtWidgets.QTextBrowser()
        self.bottomDock.setWidget(self.message_window)

    def main_panel(self):
        ##### MAIN PLOT WIDGET
        # Create Tab widget for plots
        self.plot_widgets = QtWidgets.QTabWidget()

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

    def click_plot_scan_button(self):
        # check to make sure at least one file is selected
        if self.manager.count_checked_files() < 1:
            self.message_window.append("Please select a file.")
            return

        # add scenes/plots
        self.manager.add_scene("Crop 1")
        self.manager.add_scene("Crop 2")

        # reset plot tabs and plot selected scans
        self.plot_widgets.clear()
        self.plot_widgets.addTab(self.manager.crop_1, "Crop 1")
        self.plot_widgets.addTab(self.manager.crop_2, "Crop 2")
        self.select_points_button.setEnabled(True)
        self.remove_selected_points_button.setEnabled(True)
        print("Selected files plotted.")

    def click_select_points_button(self):
        # enter select mode
        self.manager.select_points()
    
    def click_remove_selected_points_button(self):
        # remove selected points
        self.manager.remove_selected_points()
        self.save_crop_1_button.setEnabled(True)
        self.save_crop_2_button.setEnabled(True)

    def click_save_crop_1_button(self):
        # save 'Crop 1' as a new file
        save_file_path, file_type = QFileDialog.getSaveFileName()
        if save_file_path != '':
            self.manager.save_crop_1(save_file_path)

    def click_save_crop_2_button(self):
        # save 'Crop 2' as a new file
        save_file_path, file_type = QFileDialog.getSaveFileName()
        if save_file_path != '':
            self.manager.save_crop_2(save_file_path)

    def click_reset_button(self):
        # reset everything in window
        self.manager.file_manager.reset_files()
        self.plot_widgets.clear()
        self.plot_scan_button.setChecked(False)
        self.select_points_button.setChecked(False)
        self.select_points_button.setEnabled(False)
        self.remove_selected_points_button.setEnabled(False)
        self.save_crop_1_button.setEnabled(False)
        self.save_crop_2_button.setEnabled(False)