from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
# from grid import Grid
from scene import Scene
import numpy as np
import copy
from datetime import datetime
from file_manager import File_Manager
from laspy.file import File

# import tie_point_check as tpc
# import vispy.scene
# from vispy.scene import visuals
# from laspy.file import File

class crop_file_object(QWidget):
    def __init__(self, manager, file_path):
        super(QWidget, self).__init__()
        self.manager = manager
        self.file_path = file_path
        print(self.file_path)
        self.file_name = file_path.split('/')[-1]
        print(self.file_name)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        # self.checkbox_group = QButtonGroup()
        # self.checkbox_group.exclusive(True)

        self.crop_2_flag = False
        self.crop_1_flag = False

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.crop_1_checkbox = QCheckBox('Crop 1')
        self.crop_1_checkbox.stateChanged.connect(lambda:self.crop_1_check_boxes())
        # self.checkbox_group.addButton(self.crop_1_checkbox)
        self.horizontal_layout.addWidget(self.crop_1_checkbox)

        self.crop_2_checkbox = QCheckBox('Crop 2')
        self.crop_2_checkbox.stateChanged.connect(lambda:self.crop_2_check_boxes())
        # self.checkbox_group.addButton(self.crop_2_checkbox)
        self.horizontal_layout.addWidget(self.crop_2_checkbox)

        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.click_remove_button)
        self.horizontal_layout.addWidget(self.remove_button)

        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)

        self.setLayout(self.vertical_layout)

    def crop_1_check_boxes(self):
        if self.crop_1_checkbox.isChecked():
            self.manager.set_crop_1_flags(self.file_path)
            self.crop_2_checkbox.setEnabled(False)
            return
        if not self.crop_1_checkbox.isChecked():
            self.manager.unset_crop_1_flags()
            if self.manager.file_dict['Crop 2'] == None:
                self.crop_2_checkbox.setEnabled(True)

    def crop_2_check_boxes(self):
        if self.crop_2_checkbox.isChecked():
            self.manager.set_crop_2_flags(self.file_path)
            self.crop_1_checkbox.setEnabled(False)
            return
        if not self.crop_2_checkbox.isChecked():
            self.manager.unset_crop_2_flags()
            if self.manager.file_dict['Crop 1'] == None:
                self.crop_1_checkbox.setEnabled(True)

    def click_remove_button(self):
        self.manager.remove_file_from_manager(self.file_path)

class Manager:
    def __init__(self, window, file_manager):
        self.window = window
        self.file_manager = file_manager
        self.file_manager.add_manager('Crop', self)
        self.file_list = []
        self.file_dict = {'Crop 1': None, 'Crop 2': None}
        # self.files = {'Crop 1': None, 'Crop 2': None}

        self.crop_1 = None
        self.crop_2 = None
        self.crop_1_selected_areas = []
        self.crop_2_selected_areas = []

    def add_file_to_manager(self, file_path):
        self.file_manager.add_file(file_path)

    def add_file_object(self, file_path):
        print('Adding file to list', file_path)
        self.file_list.append(crop_file_object(self, file_path))
        self.clear_flags()
        self.window.left_dock()        
        if len(self.file_list) > 0:
            self.window.plot_scan_button.setEnabled(True)

    def remove_file_from_manager(self, file_path):
        self.file_manager.remove_file(file_path)
        
    def remove_file_object(self, file_path):
        print('Deleting file from list ', file_path)
        for i in range(len(self.file_list)):
            print('i', i)
            if self.file_list[i].file_path == file_path:
                pop = self.file_list.pop(i)
                print(pop.file_path)
                # self.window.file_layout.takeAt(i)
                self.clear_flags()
                self.window.files_update()
                break
        self.window.left_dock()
        

    def count_checked_files(self):
        count = 0
        for key, value in self.file_dict.items():
            if value != None:
                count += 1
        print('file count', count)
        return count

    def add_scene(self, key):
        if self.file_dict[key] != None:
            file_path = self.file_dict[key]
            print('file path', file_path)
            if key == "Crop 1": # and key in self.files.keys():
                self.crop_1 = Scene(self, 
                self.file_manager.file_dict[file_path].init_xyz,
                np.array([[1.0, 0.0, 0.0] for i in range(len(self.file_manager.file_dict[file_path].init_xyz))]),
                'Crop')

            if key == "Crop 2": # and key in self.files.keys():
                self.crop_2 = scene = Scene(self, 
                self.file_manager.file_dict[file_path].init_xyz,
                np.array([[0.0, 1.0, 0.0] for i in range(len(self.file_manager.file_dict[file_path].init_xyz))]),
                'Crop')

            print(f"{key} file added.")


    def select_points(self):
        if self.file_dict["Crop 1"] != None: # in self.files.keys():
            self.crop_1.select_flag = self.window.select_points_button.isChecked()
            self.crop_1.event_connect(self.crop_1.select_flag)
            self.crop_1.select_id = '2'
            self.crop_1.text.text = 'In rectangular select mode, press 1 to switch to lasso select'

        if self.file_dict["Crop 2"] != None: # in self.files.keys():
            self.crop_2.select_flag = self.window.select_points_button.isChecked()     
            self.crop_2.event_connect(self.crop_2.select_flag)
            self.crop_2.select_id = '2'
            self.crop_2.text.text = 'In rectangular select mode, press 1 to switch to lasso select'

    def add_selected_points(self):
        if self.file_dict["Crop 1"] != None:
            # if "Crop 1" in self.files.keys():
            selected = self.crop_1.selected
            data = selfcrop_1.data
            self.crop_1_selected_areas.append(data[selected])
            self.crop_1.permanently_mark_selected()
            print("crop 1 selected\n", self.crop_1_selected_areas)
            
        if self.file_dict["Crop 2"] != None:
            # if "Crop 2" in self.files.keys():
            selected = self.crop_2.selected
            data = self.crop_2.data
            self.crop_2_selected_areas.append(data[selected])
            self.crop_2.permanently_mark_selected()
            print("crop 2 selected\n", self.crop_2_selected_areas)

    def remove_selected_points(self):
        if self.file_dict["Crop 1"] != None:
            selected_crop_1 = self.crop_1.remove_selected_points()
            self.crop_1.reset_selected()
            if len(selected_crop_1) > 0:
                print('updating file manager')
                self.update_file_manager(selected_crop_1, self.file_dict["Crop 1"])
                selected_crop_1 = None

        if self.file_dict["Crop 2"] != None:
            selected_crop_2 = self.crop_2.remove_selected_points()
            self.crop_2.reset_selected()
            if len(selected_crop_2) > 0:
                self.update_file_manager(selected_crop_2, self.file_dict["Crop 2"])
                selected_crop_2 = None
    
    def update_file_manager(self, selected, file_path):
        self.file_manager.remove_cropped_points(selected, file_path)

    def save_crop_1(self, save_file_path):
        if self.file_dict["Crop 1"] != None:
            file_path = self.file_dict["Crop 1"]
            cropped_file = File(save_file_path, mode = "w", header = self.file_manager.file_dict[file_path].file.header)
            cropped_file.points = self.file_manager.file_dict[file_path].points
            cropped_file.x = self.file_manager.file_dict[file_path].x
            cropped_file.y = self.file_manager.file_dict[file_path].y
            cropped_file.z = self.file_manager.file_dict[file_path].z
            cropped_file.intensity = self.file_manager.file_dict[file_path].intensity
            try:
                cropped_file.red = self.file_manager.file_dict[file_path].red
                cropped_file.green = self.file_manager.file_dict[file_path].green
                cropped_file.blue = self.file_manager.file_dict[file_path].blue
            except:
                pass
            cropped_file.close()

    def save_crop_2(self, save_file_path):
        if self.file_dict["Crop 2"] != None:
            file_path = self.file_dict["Crop 2"]
            cropped_file = File(save_file_path, mode = "w", header = self.file_manager.file_dict[file_path].file.header)
            cropped_file.points = self.file_manager.file_dict[file_path].points
            cropped_file.x = self.file_manager.file_dict[file_path].x
            cropped_file.y = self.file_manager.file_dict[file_path].y
            cropped_file.z = self.file_manager.file_dict[file_path].z
            cropped_file.intensity = self.file_manager.file_dict[file_path].intensity
            try:
                cropped_file.red = self.file_manager.file_dict[file_path].red
                cropped_file.green = self.file_manager.file_dict[file_path].green
                cropped_file.blue = self.file_manager.file_dict[file_path].blue
            except:
                pass
            cropped_file.close()

    def reset_basis_info(self):
        self.grid.snow_depth_key == None
        self.grid.max_bound = None
        self.grid.min_bound = None
        return '-', '-'

    def set_crop_1_flags(self, path):
        self.file_dict['Crop 1'] = path
        print(self.file_dict['Crop 1'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Crop 1']:
                pass
            else:
                i.crop_1_checkbox.setEnabled(False)

    def unset_crop_1_flags(self):
        self.file_dict['Crop 1'] = None
        for i in self.file_list:
            if not i.crop_2_checkbox.isChecked():
                i.crop_1_checkbox.setEnabled(True)

    def set_crop_2_flags(self, path):
        self.file_dict['Crop 2'] = path
        print(self.file_dict['Crop 2'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Crop 2']:
                pass
            else:
                i.crop_2_checkbox.setEnabled(False)

    def unset_crop_2_flags(self):
        self.file_dict['Crop 2'] = None
        for i in self.file_list:
            if not i.crop_1_checkbox.isChecked():
                i.crop_2_checkbox.setEnabled(True)

    def clear_flags(self):
        self.file_dict['Crop 1'] = None
        self.file_dict['Crop 2'] = None
        for i in self.file_list:
            # uncheck
            i.crop_1_checkbox.setChecked(False)
            i.crop_2_checkbox.setChecked(False)
            # enable
            i.crop_1_checkbox.setEnabled(True)
            i.crop_2_checkbox.setEnabled(True)



