from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from grid_file import Grid_File
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

        self.alignment_flag = False
        self.base_flag = False

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.base_checkbox = QCheckBox('Base')
        self.base_checkbox.stateChanged.connect(lambda:self.base_check_boxes())
        # self.checkbox_group.addButton(self.base_checkbox)
        self.horizontal_layout.addWidget(self.base_checkbox)

        self.alignment_checkbox = QCheckBox('Alignment')
        self.alignment_checkbox.stateChanged.connect(lambda:self.alignment_check_boxes())
        # self.checkbox_group.addButton(self.alignment_checkbox)
        self.horizontal_layout.addWidget(self.alignment_checkbox)

        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)

        self.setLayout(self.vertical_layout)

    def base_check_boxes(self):
        if self.base_checkbox.isChecked():
            self.manager.set_base_flags(self.file_path)
            self.alignment_checkbox.setEnabled(False)
            return
        if not self.base_checkbox.isChecked():
            self.manager.unset_base_flags()
            if self.manager.file_dict['Alignment'] == None:
                self.alignment_checkbox.setEnabled(True)

    def alignment_check_boxes(self):
        if self.alignment_checkbox.isChecked():
            self.manager.set_alignment_flags(self.file_path)
            self.base_checkbox.setEnabled(False)
            return
        if not self.alignment_checkbox.isChecked():
            self.manager.unset_alignment_flags()
            if self.manager.file_dict['Base'] == None:
                self.base_checkbox.setEnabled(True)

class Manager:
    def __init__(self, window):
        self.window = window
        self.file_list = []
        self.file_dict = {'Base': None, 'Alignment': None}
        self.files = {}
        self.files_updated = True


    def add_file(self, file_path):
        print('Adding file to list', file_path)
        self.file_list.append(file_object(self, file_path))
        print('Length of list', len(self.file_list))

    def count_checked_files(self):
        count = 0
        for key, value in self.file_dict.items():
            if value != None:
                count += 1
        print('file count', count)
        return count

    def add_scene(self, key):
        self.files[key] = Grid_File(key, self.file_dict[key])
        if key == "Base":
            scene = Scene(self, self.files[key].init_xyz, np.array([[1.0, 0.0, 0.0] for i in range(len(self.files[key].init_xyz))]), 'ICP')

        if key == "Alignment":
            scene = Scene(self, self.files[key].init_xyz, np.array([[0.0, 1.0, 0.0] for i in range(len(self.files[key].init_xyz))]), 'ICP')

        print(f"{key} file added.")
        return scene

    def make_grid(self):
        if self.count_checked_files() > 0:
            self.window.message_window.append("Creating grid and adding points.")
            self.grid.load_files(self.file_dict)
            message = self.grid.make_grid()
            self.window.message_window.append(str(message))
            # print(self.grid.grid)
            if self.grid.grid != None:
                self.flag_vegetation()
                return True
            return False
        else:
            self.window.message_window.append("Please select files.")
            return False


    def color_points(self, upper_bound, lower_bound):
        self.window.message_window.append("Coloring points...")
        message = self.grid.color_points(upper_bound, lower_bound)
        self.window.message_window.append(message)
    
    def plot_points(self):
        if self.count_checked_files() > 0:
            scene = self.grid.plot_points()
            return scene


    def select_points(self):
        self.window.scene_1.select_flag = self.window.select_points_button.isChecked()
        self.window.scene_2.select_flag = self.window.select_points_button.isChecked()
        self.window.scene_1.event_connect(self.window.scene_1.select_flag)
        self.window.scene_2.event_connect(self.window.scene_2.select_flag)
        self.window.scene_1.select_id = '2'
        self.window.scene_2.select_id = '2'
        if self.window.select_points_button.isChecked():
            self.window.scene_1.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
            self.window.scene_2.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
        else:
            self.window.scene_1.text.text = ''
            self.window.scene_2.text.text = ''

    def set_match_area(self):
        selected = self.window.scene_1.selected
        data = self.window.scene_1.data
        self.window.scene_1_selected_areas.append(data[selected])
        self.window.scene_1.permanently_mark_selected()
        

        selected = self.window.scene_2.selected
        data = self.window.scene_2.data
        self.window.scene_2_selected_areas.append(data[selected])
        self.window.scene_2.permanently_mark_selected()

        print(self.window.scene_1_selected_areas)

    def run_alignment(self):
        scene_2_selected_area_copy = copy.deepcopy(self.window.scene_2_selected_areas)
        match, iteration, error = ia.icp_algorithm(self.window.scene_1_selected_areas, self.window.scene_2_selected_areas)

        rotation, translation = ia.calculate_rotation_translation(match, scene_2_selected_area_copy, match)

        self.window.scene_2_matched_data = copy.deepcopy(self.window.scene_2.data)

        for i in range(len(self.window.scene_2_matched_data)):
            self.window.scene_2_matched_data[i] = np.matmul(rotation, self.window.scene_2_matched_data[i]) + translation

        # tpc.tie_point_error(self.window.scene_1.data, self.window.scene_2.data, self.window.scene_2_matched_data)
        points = [self.window.scene_1_selected_areas, match, scene_2_selected_area_copy]
        color = ['red', 'white', 'green']
        self.add_multi_scene(points, color, 'Selected Point Match')

        points = [self.window.scene_1.data, self.window.scene_2_matched_data, self.window.scene_2.data]
        self.add_multi_scene(points, color, 'Match Comparison')

        # canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        # view = canvas.central_widget.add_view()
        # scatter = visuals.Markers()
        # scatter.set_data(self.window.scene_1_selected_areas, edge_color = None, face_color = "red", size = 4)
        # view.add(scatter)
        # scatter2 = visuals.Markers()
        # scatter2.set_data(match, edge_color = None, face_color = "blue", size = 4)
        # view.add(scatter2)
        # scatter3 = visuals.Markers()
        # scatter3.set_data(scene_2_selected_area_copy, edge_color = None, face_color = "green", size = 4)
        # view.add(scatter3)
        # view.camera = 'arcball'
        # axis = visuals.XYZAxis(parent=view.scene)
        # vispy.app.run()

        # canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        # view = canvas.central_widget.add_view()
        # scatter = visuals.Markers()
        # scatter.set_data(self.window.scene_1.data, edge_color = None, face_color = "red", size = 4)
        # view.add(scatter)
        # scatter2 = visuals.Markers()
        # scatter2.set_data(self.window.scene_2_matched_data, edge_color = None, face_color = "blue", size = 4)
        # view.add(scatter2)
        # scatter3 = visuals.Markers()
        # scatter3.set_data(self.window.scene_2.data, edge_color = None, face_color = "green", size = 4)
        # view.add(scatter3)
        # view.camera = 'arcball'
        # axis = visuals.XYZAxis(parent=view.scene)
        # vispy.app.run()


        # aligned_file_name = self.files['Alignment'].file_name +"_aligned.las" #file_dict['Alignment'].split('/')[-1] +"_aligned.las"
        # aligned_file = File(aligned_file_name, mode = "w", header = self.files['Alignment'].file.header)
        # aligned_file.x = self.window.scene_2_matched_data[:,0]
        # aligned_file.y = self.window.scene_2_matched_data[:,1]
        # aligned_file.z = self.window.scene_2_matched_data[:,2]
        # aligned_file.close()

    def add_multi_scene(self, points, color, title):
        multi_scene = Multi_Scene(points, color, title)

        self.window.plot_widgets.addTab(multi_scene, title)

    def save_matched_file(self):
        now = datetime.now()
        date = now.strftime("%D").replace('/','-')
        time = now.strftime("%H-%M")
        aligned_file_name = self.files['Alignment'].file_name +'_aligned_to_'+self.files['Base'].file_name+"_"+date+'.las'
        aligned_file = File(aligned_file_name, mode = "w", header = self.files['Alignment'].file.header)
        aligned_file.x = self.window.scene_2_matched_data[:,0]
        aligned_file.y = self.window.scene_2_matched_data[:,1]
        aligned_file.z = self.window.scene_2_matched_data[:,2]
        aligned_file.close()

    def reset_basis_info(self):
        self.grid.snow_depth_key == None
        self.grid.max_bound = None
        self.grid.min_bound = None
        return '-', '-'

    def set_base_flags(self, path):
        self.file_dict['Base'] = path
        print(self.file_dict['Base'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Base']:
                pass
            else:
                i.base_checkbox.setEnabled(False)

    def unset_base_flags(self):
        self.file_dict['Base'] = None
        for i in self.file_list:
            if not i.alignment_checkbox.isChecked():
                i.base_checkbox.setEnabled(True)

    def set_alignment_flags(self, path):
        self.file_dict['Alignment'] = path
        print(self.file_dict['Alignment'])
        for i in self.file_list:
            if i.file_path == self.file_dict['Alignment']:
                pass
            else:
                i.alignment_checkbox.setEnabled(False)

    def unset_alignment_flags(self):
        self.file_dict['Alignment'] = None
        for i in self.file_list:
            if not i.base_checkbox.isChecked():
                i.alignment_checkbox.setEnabled(True)

    def clear_flags(self):
        self.file_dict['Base'] = None
        self.file_dict['Alignment'] = None
        for i in self.file_list:
            # uncheck
            i.base_checkbox.setChecked(False)
            i.alignment_checkbox.setChecked(False)
            # enable
            i.base_checkbox.setEnabled(True)
            i.alignment_checkbox.setEnabled(True)



