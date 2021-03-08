from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from file_manager import File_Manager
from scene import Scene


class file_object(QWidget):
    def __init__(self, manager, file_path):
        super(QWidget, self).__init__()
        self.manager = manager
        self.file_path = file_path
        print(self.file_path)
        self.file_name = file_path.split('/')[-1]
        print(self.file_name)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.ground_checkbox = QCheckBox('Ground')
        self.ground_checkbox.stateChanged.connect(lambda:self.ground_check_boxes())
        # self.checkbox_group.addButton(self.ground_checkbox)
        self.horizontal_layout.addWidget(self.ground_checkbox)

        self.intSnow_checkbox = QCheckBox('Int. Snow')
        self.intSnow_checkbox.stateChanged.connect(lambda:self.intSnow_check_boxes())
        # self.checkbox_group.addButton(self.intSnow_checkbox)
        self.horizontal_layout.addWidget(self.intSnow_checkbox)

        self.newSnow_checkbox = QCheckBox('New Snow')
        self.newSnow_checkbox.stateChanged.connect(lambda:self.newSnow_check_boxes())
        # self.checkbox_group.addButton(self.newSnow_checkbox)
        self.horizontal_layout.addWidget(self.newSnow_checkbox)

        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.click_remove_button)
        self.horizontal_layout.addWidget(self.remove_button)

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
            if self.manager.file_dict['Int. Snow'] == None:
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
            if self.manager.file_dict['Int. Snow'] == None:
                self.intSnow_checkbox.setEnabled(True)
    
    def click_remove_button(self):
        self.manager.remove_file_from_manager(self.file_path)

class Manager:
    def __init__(self, window, file_manager):
        self.window = window
        self.file_manager = file_manager
        self.file_manager.add_manager('Depth', self)
        self.file_list = []
        self.file_dict = {'Ground': None, 'Int. Snow': None, 'New Snow': None}
        self.grid = Grid(self)
        self.scene = None
        self.scan_basis = None
        self.color_basis = None
        self.stats_key = None

    def add_file_to_manager(self, file_path):
        self.file_manager.add_file(file_path)

    def add_file_object(self, file_path):
        print('Adding file to depth list', file_path)
        self.file_list.append(file_object(self, file_path))
        self.clear_flags()
        self.window.left_dock()
        if len(self.file_list) > 0:
            self.window.vegetation_button.setEnabled(True)

    def remove_file_from_manager(self, file_path):
        self.file_manager.remove_file(file_path)
        
    def remove_file_object(self, file_path):
        print('Deleting file from list ', file_path)
        for i in range(len(self.file_list)):
            print('i', i)
            if self.file_list[i].file_path == file_path:
                pop = self.file_list.pop(i)
                print(pop.file_path)
                self.clear_flags()
                self.window.files_update()
                break
        self.window.left_dock()
            
        print('file list', self.file_list)

    def count_checked_files(self):
        count = 0
        for key, value in self.file_dict.items():
            if value != None:
                count += 1
        print('file count', count)
        return count

    def make_grid(self):
        if self.count_checked_files() > 0:
            print('file dict \n', self.file_dict)
            self.window.message_window.append("Creating grid and adding points.")
            self.grid.reset_files()
            for key, value in self.file_dict.items():
                if value != None:
                    self.grid.add_data(key, self.file_manager.file_dict[value])

            # self.grid.load_files(self.file_dict)
            message = self.grid.make_grid()
            self.window.message_window.append(str(message))
            if self.grid.grid != None:
                self.flag_vegetation()
                return True
            return False
        else:
            self.window.message_window.append("Please select files.")
            return False

    def flag_vegetation(self):
        if self.count_checked_files() > 0:
            self.window.message_window.append("Flagging vegetation.")
            counts = self.grid.flag_vegetation()
            for key in counts:
                self.window.message_window.append(str(key) + " scan has " + str(counts[key]) + " cells with vegetation")

    def calculate_snow_depth(self):
        if self.count_checked_files() > 1:
            self.window.message_window.append("Calculating snow depth...")
            average_depths = self.grid.calculate_snow_depth()
            for key in average_depths:
                self.window.message_window.append("New snow scan has a depth of " + str(round(average_depths[key]*3.28, 3)) + " feet to " + str(key) + " scan.")
        else:
            self.window.message_window.append("Please select files.")

    def color_and_plot_points(self, color_basis, scan_basis, upper_bound, lower_bound):
        self.window.message_window.append("Coloring points...")
        xyz, rgb, upper_bound, lower_bound = self.grid.color_points(color_basis, scan_basis, upper_bound, lower_bound)
        self.scene = Scene(self.grid, xyz, rgb, color_basis)
        return self.scene, upper_bound, lower_bound

    def select_points(self):
        self.scene.select_flag = self.window.select_points_button.isChecked()
        self.scene.event_connect(self.scene.select_flag)
        self.scene.select_id = '2'
        if self.window.select_points_button.isChecked():
            self.scene.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
        else:
            self.scene.text.text = ''

    def get_basis_info(self, color_basis, scan_basis):
        if self.file_dict[scan_basis] == None:
            return '-', '-'
        
        if color_basis == 'intensity':
            max_bound, min_bound = self.grid.get_max_and_min_intensity(scan_basis)

        if color_basis == 'depth':
            max_bound, min_bound = self.grid.get_max_and_min_depth(scan_basis)
        return max_bound, min_bound

    def reset_basis_info(self):
        max_bound, min_bound = self.grid.reset_basis_info()
        return max_bound, min_bound

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
        self.file_dict['Int. Snow'] = path
        print(self.file_dict['Int. Snow'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Int. Snow']:
                pass
            else:
                i.intSnow_checkbox.setEnabled(False)

    def unset_intSnow_flags(self):
        self.file_dict['Int. Snow'] = None
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
        self.file_dict['Int. Snow'] = None
        self.file_dict['New Snow'] = None
        for i in self.file_list:
            i.ground_checkbox.setChecked(False)
            i.intSnow_checkbox.setChecked(False)
            i.newSnow_checkbox.setChecked(False)
            i.ground_checkbox.setEnabled(True)
            i.intSnow_checkbox.setEnabled(True)
            i.newSnow_checkbox.setEnabled(True)


