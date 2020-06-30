from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid2 import Grid


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

        self.snow_flag = False
        self.base_flag = False
        self.summer_flag = False

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.summer_checkbox = QCheckBox("Summer")
        self.summer_checkbox.stateChanged.connect(lambda:self.summer_check_boxes())
        # self.checkbox_group.addButton(self.summer_checkbox)
        self.horizontal_layout.addWidget(self.summer_checkbox)

        self.base_checkbox = QCheckBox("Base")
        self.base_checkbox.stateChanged.connect(lambda:self.base_check_boxes())
        # self.checkbox_group.addButton(self.base_checkbox)
        self.horizontal_layout.addWidget(self.base_checkbox)

        self.snow_checkbox = QCheckBox("Snow")
        self.snow_checkbox.stateChanged.connect(lambda:self.snow_check_boxes())
        # self.checkbox_group.addButton(self.snow_checkbox)
        self.horizontal_layout.addWidget(self.snow_checkbox) 

        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)

        self.setLayout(self.vertical_layout)

    def summer_check_boxes(self):
        if self.summer_checkbox.isChecked():
            self.manager.set_summer_flags(self.file_path)
            self.base_checkbox.setEnabled(False)
            self.snow_checkbox.setEnabled(False)
            return
        if not self.summer_checkbox.isChecked():
            self.manager.unset_summer_flags()
            self.base_checkbox.setEnabled(True)
            self.snow_checkbox.setEnabled(True)

    def base_check_boxes(self):
        if self.base_checkbox.isChecked():
            self.manager.set_base_flags(self.file_path)
            self.summer_checkbox.setEnabled(False)
            self.snow_checkbox.setEnabled(False)
            return
        if not self.base_checkbox.isChecked():
            self.manager.unset_base_flags()
            self.summer_checkbox.setEnabled(True)
            self.snow_checkbox.setEnabled(True)

    def snow_check_boxes(self):
        if self.snow_checkbox.isChecked():
            self.manager.set_snow_flags(self.file_path)
            self.summer_checkbox.setEnabled(False)
            self.base_checkbox.setEnabled(False)
            return
        if not self.snow_checkbox.isChecked():
            self.manager.unset_snow_flags()
            self.summer_checkbox.setEnabled(True)
            self.base_checkbox.setEnabled(True)
            
class Manager:
    def __init__(self):
        self.file_list = []
        # self.file_dict = {}
        # self.file_dict['summer'] = None
        # self.file_dict['base'] = None
        # self.file_dict['snow'] = None
        self.snow_file = None
        self.base_file = None
        self.summer_file = None
        self.files_updated = True
        # self.grid = Grid(self)

    def add_file(self, file_path):
        print('Adding file to list', file_path)
        self.file_list.append(file_object(self, file_path))
        print('Length of list', len(self.file_list))

    def set_summer_flags(self, path):
        self.summer_file = path
        print(self.summer_file)
        for i in self.file_list:
            if i.file_path == self.summer_file:
                pass
            else:
                i.summer_checkbox.setEnabled(False)

    def unset_summer_flags(self):
        self.summer_file = None
        for i in self.file_list:
            i.summer_checkbox.setEnabled(True)


    def set_base_flags(self, path):
        self.base_file = path
        print(self.base_file)
        for i in self.file_list:
            if i.file_path == self.base_file:
                pass
            else:
                i.base_checkbox.setEnabled(False)

    def unset_base_flags(self):
        self.base_file = None
        for i in self.file_list:
            i.base_checkbox.setEnabled(True)

    def set_snow_flags(self, path):
        self.snow_file = path
        print(self.snow_file)
        for i in self.file_list:
            if i.file_path == self.snow_file:
                pass
            else:
                i.snow_checkbox.setEnabled(False)

    def unset_snow_flags(self):
        self.snow_file = None
        for i in self.file_list:
            i.snow_checkbox.setEnabled(True)


