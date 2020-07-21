from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid


class file_object(QWidget):
    def __init__(self, manager, path):
        super(QWidget, self).__init__()
        self.manager = manager
        self.file_path = path
        print(self.file_path)
        self.file_name = path.split('/')[-1]
        print(self.file_name)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        # self.checkbox_group = QButtonGroup()
        # self.checkbox_group.exclusive(True)

        self.newSnow_flag = False
        self.intSnow_flag = False
        self.ground_flag = False

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.ground_checkbox = QCheckBox('Ground')
        self.ground_checkbox.stateChanged.connect(lambda:self.ground_check_boxes())
        # self.checkbox_group.addButton(self.ground_checkbox)
        self.horizontal_layout.addWidget(self.ground_checkbox)

        self.intSnow_checkbox = QCheckBox('Inter. Snow')
        self.intSnow_checkbox.stateChanged.connect(lambda:self.intSnow_check_boxes())
        # self.checkbox_group.addButton(self.intSnow_checkbox)
        self.horizontal_layout.addWidget(self.intSnow_checkbox)

        self.newSnow_checkbox = QCheckBox('New Snow')
        self.newSnow_checkbox.stateChanged.connect(lambda:self.newSnow_check_boxes())
        # self.checkbox_group.addButton(self.newSnow_checkbox)
        self.horizontal_layout.addWidget(self.newSnow_checkbox) 

        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)

        self.setLayout(self.vertical_layout)

    def ground_check_boxes(self):
        if self.ground_checkbox.isChecked():
            self.manager.set_ground_flags(self.file_path)
            self.intSnow_checkbox.setEnabled(False)
            self.newSnow_checkbox.setEnabled(False)
            return
        if not self.ground_checkbox.isChecked():
            self.manager.unset_ground_flags()
            if self.manager.file_dict['Inter. Snow'] == None:
                self.intSnow_checkbox.setEnabled(True)
            if self.manager.file_dict['New Snow'] == None:
                self.newSnow_checkbox.setEnabled(True)

    def intSnow_check_boxes(self):
        if self.intSnow_checkbox.isChecked():
            self.manager.set_intSnow_flags(self.file_path)
            self.ground_checkbox.setEnabled(False)
            self.newSnow_checkbox.setEnabled(False)
            return
        if not self.intSnow_checkbox.isChecked():
            self.manager.unset_intSnow_flags()
            if self.manager.file_dict['Ground'] == None:
                self.ground_checkbox.setEnabled(True)
            if self.manager.file_dict['New Snow'] == None:
                self.newSnow_checkbox.setEnabled(True)

    def newSnow_check_boxes(self):
        if self.newSnow_checkbox.isChecked():
            self.manager.set_newSnow_flags(self.file_path)
            self.ground_checkbox.setEnabled(False)
            self.intSnow_checkbox.setEnabled(False)
            return
        if not self.newSnow_checkbox.isChecked():
            self.manager.unset_newSnow_flags()
            if self.manager.file_dict['Ground'] == None:
                self.ground_checkbox.setEnabled(True)
            if self.manager.file_dict['Inter. Snow'] == None:
                self.intSnow_checkbox.setEnabled(True)
            
class Manager:
    def __init__(self, window):
        self.window = window
        self.file_list = []
        self.file_dict = {'Ground': None, 'Inter. Snow': None, 'New Snow': None}
        self.files_updated = True
        self.grid = Grid(self)

    def add_file(self, file_path):
        print('Adding file to list', file_path)
        self.file_list.append(file_object(self, file_path))
        print('Length of list', len(self.file_list))

    def make_grid(self):
        if len(self.file_list) > 0:
            self.window.message_window.append("Creating grid and adding points.")
            self.grid.load_files(self.file_dict)
            num_cells = self.grid.make_grid()
            self.window.message_window.append("Grid Complete!")
            self.window.message_window.append(str(num_cells) + " Total Grid Cells")
            self.flag_vegetation
        else:
            self.window.message_window.append("Please select files.")

    def flag_vegetation(self):
        if len(self.file_list) > 0:
            self.window.message_window.append("Flagging vegetation.")
            counts = self.grid.flag_vegetation()
            for key in counts:
                self.window.message_window.append(str(key) + " scan has " + str(counts[key]) + " cells with vegetation")

    def calculate_snow_depth(self):
        if len(self.file_list) > 1:
            self.window.message_window.append("Calculating snow depth...")
            average_depths = self.grid.calculate_snow_depth()
            for key in average_depths:
                self.window.message_window.append("New snow scan has a depth of " + str(average_depths[key]) + " to " + str(key) + " scan.")
        else:
            self.window.message_window.append("Please select files.")

    def color_points(self):
        self.window.message_window.append("Coloring points...")
        message = self.grid.color_points()
        self.window.message_window.append(message)
    
    def plot_points(self):
        if len(self.file_list) > 0:
            plot = self.grid.plot_points()
            return plot

    def get_ground_basis_info(self):
        self.grid.snow_depth_key = 'Ground'
        max_bound, min_bound = self.grid.get_max_and_min_depth()
        return max_bound, min_bound

    def get_intSnow_basis_info(self):
        self.grid.snow_depth_key = 'Inter. Snow'
        max_bound, min_bound = self.grid.get_max_and_min_depth()
        return max_bound, min_bound

    def reset_basis_info(self):
        self.grid.snow_depth_key == None
        self.grid.max_bound = None
        self.grid.min_bound = None
        return '-', '-'

    def set_ground_flags(self, path):
        self.file_dict['Ground'] = path
        print(self.file_dict['Ground'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Ground']:
                pass
            else:
                i.ground_checkbox.setEnabled(False)

    def unset_ground_flags(self):
        self.file_dict['Ground'] = None
        for i in self.file_list:
            if not i.intSnow_checkbox.isChecked() and not i.newSnow_checkbox.isChecked():
                i.ground_checkbox.setEnabled(True)


    def set_intSnow_flags(self, path):
        self.file_dict['Inter. Snow'] = path
        print(self.file_dict['Inter. Snow'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Inter. Snow']:
                pass
            else:
                i.intSnow_checkbox.setEnabled(False)

    def unset_intSnow_flags(self):
        self.file_dict['Inter. Snow'] = None
        for i in self.file_list:
            if not i.ground_checkbox.isChecked() and not i.newSnow_checkbox.isChecked():
                i.intSnow_checkbox.setEnabled(True)

    def set_newSnow_flags(self, path):
        self.file_dict['New Snow'] = path
        print(self.file_dict['New Snow'])
        for i in self.file_list:
            if i.file_path == self.file_dict['New Snow']:
                pass
            else:
                i.newSnow_checkbox.setEnabled(False)

    def unset_newSnow_flags(self):
        self.file_dict['New Snow'] = None
        for i in self.file_list:
            if not i.ground_checkbox.isChecked() and not i.intSnow_checkbox.isChecked():
                i.newSnow_checkbox.setEnabled(True)

    def clear_flags(self):
        self.file_dict['Ground'] = None
        self.file_dict['Inter. Snow'] = None
        self.file_dict['New Snow'] = None
        for i in self.file_list:
            i.ground_checkbox.setChecked(False)
            i.intSnow_checkbox.setChecked(False)
            i.newSnow_checkbox.setChecked(False)
            i.ground_checkbox.setEnabled(True)
            i.intSnow_checkbox.setEnabled(True)
            i.newSnow_checkbox.setEnabled(True)


