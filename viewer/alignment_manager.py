from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from scene import Scene
from multi_scene import Multi_Scene
import numpy as np
import ICP_algorithm as ia
import copy
from datetime import datetime

import tie_point_check as tpc
import vispy.scene
from vispy.scene import visuals
from laspy.file import File
from grid import Grid

class file_object(QWidget):
    ### This object is what will be displayed in the window on the left hand side when each file is loaded in
    def __init__(self, manager, file_path):
        super(QWidget, self).__init__()
        # point to manager
        self.manager = manager
        # store file path
        self.file_path = file_path
        print(self.file_path)
        # get name from path
        self.file_name = file_path.split('/')[-1]
        print(self.file_name)
        
        # initialize layouts
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()

        # initialize flags
        self.alignment_flag = False
        self.base_flag = False

        ### create/add widgets to layout
        # file name
        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        # base checkbox
        self.base_checkbox = QCheckBox('Base')
        self.base_checkbox.stateChanged.connect(lambda:self.base_check_boxes())
        self.horizontal_layout.addWidget(self.base_checkbox)

        # alignment checkbox
        self.alignment_checkbox = QCheckBox('Alignment')
        self.alignment_checkbox.stateChanged.connect(lambda:self.alignment_check_boxes())
        self.horizontal_layout.addWidget(self.alignment_checkbox)

        # remove button
        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.click_remove_button)
        self.horizontal_layout.addWidget(self.remove_button)

        # overall widgets for object layout
        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)
        self.setLayout(self.vertical_layout)

    def base_check_boxes(self):
        ### function tied to 'Base' heckboxes
        if self.base_checkbox.isChecked():
            self.manager.set_base_flags(self.file_path)
            self.alignment_checkbox.setEnabled(False)
            return
        if not self.base_checkbox.isChecked():
            self.manager.unset_base_flags()
            if self.manager.file_dict['Alignment'] == None:
                self.alignment_checkbox.setEnabled(True)

    def alignment_check_boxes(self):
        ### function tied to 'Alignment' heckboxes
        if self.alignment_checkbox.isChecked():
            self.manager.set_alignment_flags(self.file_path)
            self.base_checkbox.setEnabled(False)
            return
        if not self.alignment_checkbox.isChecked():
            self.manager.unset_alignment_flags()
            if self.manager.file_dict['Base'] == None:
                self.base_checkbox.setEnabled(True)

    def click_remove_button(self):
        ### funtion to remove file from application if 'Remove' button is clicked
        self.manager.remove_file_from_manager(self.file_path)

class Manager:
    def __init__(self, window, file_manager):
        ### initialize attributes
        # point to main window
        self.window = window
        # point to master manager
        self.file_manager = file_manager
        # add self(alignment manager) to the master manager
        self.file_manager.add_manager('Align', self)
        # list of files loaded
        self.file_list = []
        # dictionary of alignment file assignments
        self.file_dict = {'Base': None, 'Alignment': None}

    def add_file_to_manager(self, file_path):
        # add file to master manager
        self.file_manager.add_file(file_path)

    def add_file_object(self, file_path):
        # add file object to alignment window
        print('Adding file to list', file_path)
        self.file_list.append(file_object(self, file_path))
        self.clear_flags()
        self.window.left_dock()
        # enable functions in window
        if len(self.file_list) > 1:
            self.window.add_match_area_button.setEnabled(True)
            self.window.color_vegetation_checkbox.setEnabled(True)
            self.window.color_default_checkbox.setEnabled(True)
            # self.window.alignment_default_checkbox.setEnabled(True)

    def remove_file_from_manager(self, file_path):
        # remove file from master manager
        self.file_manager.remove_file(file_path)

    def remove_file_object(self, file_path):
        # remove file object from alignment window
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
        # count number of selected files
        count = 0
        for key, value in self.file_dict.items():
            if value != None:
                count += 1
        print('file count', count)
        return count

    def add_scene(self, key):
        ### plot las file
        if self.file_dict[key] != None:
            file_path = self.file_dict[key]
            if key == "Base":
                # plot 'base' file
                self.base_grid = Grid(self)
                self.base_grid.add_data('New Snow', self.file_manager.file_dict[file_path])
                self.base_grid.make_grid()
                self.base_grid.flag_vegetation()
                self.base_grid.color_points('default', 'New Snow', 0, 0)

                if self.window.color_basis == 'vegetation':
                    color = np.stack((self.file_manager.file_dict[file_path].plot_red/max(self.file_manager.file_dict[file_path].plot_red),
                    self.file_manager.file_dict[file_path].plot_green/max(self.file_manager.file_dict[file_path].plot_green), 
                    self.file_manager.file_dict[file_path].plot_blue/max(self.file_manager.file_dict[file_path].plot_blue)))
                    color = np.transpose(color)

                else: 
                    color = np.array([[1.0, 0.0, 0.0] for i in range(len(self.file_manager.file_dict[file_path].init_xyz))])
                scene = Scene(self,
                 self.file_manager.file_dict[file_path].init_xyz,
                 color,
                 'ICP')

            if key == "Alignment":
                # plot 'alignment' file
                self.alignment_grid = Grid(self)
                self.alignment_grid.add_data('New Snow', self.file_manager.file_dict[file_path])
                self.alignment_grid.make_grid()
                self.alignment_grid.flag_vegetation()
                self.alignment_grid.color_points('default', 'New Snow', 0, 0)
                
                if self.window.color_basis == 'vegetation':
                    color = np.stack((self.file_manager.file_dict[file_path].plot_red/max(self.file_manager.file_dict[file_path].plot_red),
                    self.file_manager.file_dict[file_path].plot_green/max(self.file_manager.file_dict[file_path].plot_green), 
                    self.file_manager.file_dict[file_path].plot_blue/max(self.file_manager.file_dict[file_path].plot_blue)))
                    color = np.transpose(color)

                else: 
                    color = np.array([[0.0, 1.0, 0.0] for i in range(len(self.file_manager.file_dict[file_path].init_xyz))])
                scene = Scene(self,
                 self.file_manager.file_dict[file_path].init_xyz,
                 color,
                 'ICP')

            print(f"{key} file added.")
            return scene

    def select_points(self):
        # set 'select points' flag to button state 
        self.window.scene_1.select_flag = self.window.select_points_button.isChecked()
        self.window.scene_2.select_flag = self.window.select_points_button.isChecked()
        # connect event to window
        self.window.scene_1.event_connect(self.window.scene_1.select_flag)
        self.window.scene_2.event_connect(self.window.scene_2.select_flag)
        # start with rectangular select
        self.window.scene_1.select_id = '2'
        self.window.scene_2.select_id = '2'
        # Add text to window
        if self.window.select_points_button.isChecked():
            self.window.scene_1.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
            self.window.scene_2.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
        else:
            self.window.scene_1.text.text = ''
            self.window.scene_2.text.text = ''

    def set_match_area(self):
        ### save selected areas for matching
        selected = self.window.scene_1.selected
        if selected != []:
            data = self.window.scene_1.data
            self.window.scene_1_selected_areas.append(data[selected])
            self.window.scene_1.permanently_mark_selected()
        
        selected = self.window.scene_2.selected
        if selected != []:
            data = self.window.scene_2.data
            self.window.scene_2_selected_areas.append(data[selected])
            self.window.scene_2.permanently_mark_selected()

    def run_alignment(self):
        if self.window.alignment_basis == 'selection':
            ### Remove Duplicates
            ## Scene 1
            unique_points, unique_indices = np.unique(self.window.scene_1_selected_areas, return_index=True, axis=0)
            self.window.scene_1_selected_areas = self.window.scene_1_selected_areas[unique_indices]
            ## Scene 2
            unique_points, unique_indices = np.unique(self.window.scene_2_selected_areas, return_index=True, axis=0)
            self.window.scene_2_selected_areas = self.window.scene_2_selected_areas[unique_indices]

        if self.window.alignment_basis == 'default':
            ## get idices of the vegetation points
            scene_1_indices = self.base_grid.get_vegetation_indices()
            scene_2_indices = self.alignment_grid.get_vegetation_indices()
            ## get vegetation points
            self.window.scene_1_selected_areas = self.window.scene_1.data[scene_1_indices]
            self.window.scene_2_selected_areas = self.window.scene_2.data[scene_2_indices]

        # copy original points in case match is discarded
        scene_2_selected_area_copy = copy.deepcopy(self.window.scene_2_selected_areas)

        # run algorithms
        match, iteration, error = ia.icp_algorithm(self.window.scene_1_selected_areas, self.window.scene_2_selected_areas)

        # get rotation and translation
        rotation, translation = ia.calculate_rotation_translation(match, scene_2_selected_area_copy, match)

        # copy points to apply rotation in case match is kept
        self.window.scene_2_matched_data = copy.deepcopy(self.window.scene_2.data)

        # apply rotation to get match
        for i in range(len(self.window.scene_2_matched_data)):
            self.window.scene_2_matched_data[i] = np.matmul(rotation, self.window.scene_2_matched_data[i]) + translation

        # tpc.tie_point_error(self.window.scene_1.data, self.window.scene_2.data, self.window.scene_2_matched_data)

        # plot alignment points: base, original, and match in new window
        points = [self.window.scene_1_selected_areas, match, scene_2_selected_area_copy]
        color = ['red', 'white', 'green']
        self.add_multi_scene(points, color, 'Selected Point Match')

        # plot full scans:  base, original, and match in new window
        points = [self.window.scene_1.data, self.window.scene_2_matched_data, self.window.scene_2.data]
        self.add_multi_scene(points, color, 'Match Comparison')

    def add_multi_scene(self, points, color, title):
        ### plot multi scene and add it to window
        multi_scene = Multi_Scene(points, color, title)
        self.window.plot_widgets.addTab(multi_scene, title)

    def set_alignment(self):
        ### if alignment is accepted this will update the points in the master file manager
        file_path = self.file_dict['Alignment']
        self.file_manager.update_aligned_points(self.window.scene_2_matched_data, file_path)

    def save_matched_file(self, save_file_path):
        ### save the alignment match as a new las file
        if self.file_dict['Alignment'] != None:
            aligned_file_path = self.file_dict['Alignment']
            aligned_file = File(save_file_path, mode = "w", header = self.file_manager.file_dict[aligned_file_path].file.header)
            aligned_file.points = self.file_manager.file_dict[aligned_file_path].points
            aligned_file.x = self.file_manager.file_dict[aligned_file_path].x
            aligned_file.y = self.file_manager.file_dict[aligned_file_path].y
            aligned_file.z = self.file_manager.file_dict[aligned_file_path].z
            aligned_file.intensity = self.file_manager.file_dict[aligned_file_path].intensity
            try:
                aligned_file.red = self.file_manager.file_dict[aligned_file_path].red
                aligned_file.green = self.file_manager.file_dict[aligned_file_path].green
                aligned_file.blue = self.file_manager.file_dict[aligned_file_path].blue
            except:
                pass
            aligned_file.close()

    def reset_basis_info(self):
        # reset all flags
        self.grid.snow_depth_key == None
        self.grid.max_bound = None
        self.grid.min_bound = None
        return '-', '-'

    def set_base_flags(self, path):
        # if a file is set as 'Base' un-enable the 'Base' checkbox for other loaded files
        self.file_dict['Base'] = path
        print(self.file_dict['Base'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Base']:
                pass
            else:
                i.base_checkbox.setEnabled(False)

    def unset_base_flags(self):
        # if a file is unset as 'Base' enable the 'Base' checkbox for other loaded files
        self.file_dict['Base'] = None
        for i in self.file_list:
            if not i.alignment_checkbox.isChecked():
                i.base_checkbox.setEnabled(True)

    def set_alignment_flags(self, path):
        # if a file is set as 'Alignment' un-enable the 'Alignment' checkbox for other loaded files
        self.file_dict['Alignment'] = path
        print(self.file_dict['Alignment'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Alignment']:
                pass
            else:
                i.alignment_checkbox.setEnabled(False)

    def unset_alignment_flags(self):
        # if a file is unset as 'Alignment' enable the 'Alignment' checkbox for other loaded files
        self.file_dict['Alignment'] = None
        for i in self.file_list:
            if not i.base_checkbox.isChecked():
                i.alignment_checkbox.setEnabled(True)

    def clear_flags(self):
        # reset all flags
        self.file_dict['Base'] = None
        self.file_dict['Alignment'] = None
        for i in self.file_list:
            # uncheck
            i.base_checkbox.setChecked(False)
            i.alignment_checkbox.setChecked(False)
            # enable
            i.base_checkbox.setEnabled(True)
            i.alignment_checkbox.setEnabled(True)



