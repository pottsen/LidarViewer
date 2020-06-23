from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid


class file_object(QWidget):
    def __init__(self, path):
        super(QWidget, self).__init__()
        self.file_path = path
        print(self.file_path)
        self.file_name = path.split('/')[-1]
        print(self.file_name)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        self.checkbox_group = QButtonGroup()
        # self.checkbox_group.exclusive(True)

        self.snow_flag = False
        self.base_flag = False
        self.summer_flag = False

        self.name_widget = QLabel(str(self.file_name))    
        self.vertical_layout.addWidget(self.name_widget) 

        self.summer_checkbox = QCheckBox("Summer")
        self.checkbox_group.addButton(self.summer_checkbox)
        self.horizontal_layout.addWidget(self.summer_checkbox)

        self.base_checkbox = QCheckBox("Base")
        self.checkbox_group.addButton(self.base_checkbox)
        self.horizontal_layout.addWidget(self.base_checkbox)

        self.snow_checkbox = QCheckBox("Snow")
        self.checkbox_group.addButton(self.snow_checkbox)
        self.horizontal_layout.addWidget(self.snow_checkbox) 

        self.horizontal_file_widget = QWidget()
        self.horizontal_file_widget.setLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.horizontal_file_widget)

        self.setLayout(self.vertical_layout)
            
class Manager:
    def __init__(self):
        self.file_list = []
        self.snow_file = None
        self.base_file = None
        self.summer_file = None
        self.files_updated = True

    def add_file(self, file_path):
        print('Adding file to list', file_path)
        self.file_list.append(file_object(file_path))
        print('Length of list', len(self.file_list))

    def check_flags(self):
        self.snow_file = None
        self.base_file = None
        self.summer_file = None
        for i in range(len(self.file_list)):
            print(self.file_list[i].summer_checkbox.isChecked())
            print(self.file_list[i].base_checkbox.isChecked())
            print(self.file_list[i].snow_checkbox.isChecked())

            if self.file_list[i].summer_checkbox.isChecked():
                self.file_list[i].summer_flag = True
            else:
                self.file_list[i].summer_flag = False

            if self.file_list[i].base_checkbox.isChecked():
                self.file_list[i].base_flag = True
            else:
                self.file_list[i].base_flag = False  

            if self.file_list[i].snow_checkbox.isChecked():
                self.file_list[i].snow_flag = True
            else:
                self.file_list[i].snow_flag = False   

            # if self.file_list[i].snow_flag and self.file_list[i].base_flag:
            #     print(str("Choose one option per file: " + self.file_list[i].file_name))
            #     return False, str("Choose one option per file: " + self.file_list[i].file_name)
            # elif self.file_list[i].snow_flag and self.file_list[i].summer_flag:
            #     print(str("Choose one option per file: " + self.file_list[i].file_name))
            #     return False, str("Choose one option per file: " + self.file_list[i].file_name)
            # elif self.file_list[i].summer_flag and self.file_list[i].base_flag:
            #     print(str("Choose one option per file: " + self.file_list[i].file_name))
            #     return False, str("Choose one option per file: " + self.file_list[i].file_name)
            # else:
            if self.file_list[i].summer_flag and self.summer_file == None:
                self.summer_file = self.file_list[i].file_path
            elif self.file_list[i].summer_flag and self.summer_file != None:
                return False, str('Select only one summer scan')
            
            if self.file_list[i].base_flag and self.summer_file == None:
                self.base_file = self.file_list[i].file_path
            elif self.file_list[i].base_flag and self.summer_file != None:
                return False, str('Select only one base scan')
            
            if self.file_list[i].snow_flag and self.summer_file == None:
                self.snow_file = self.file_list[i].file_path
            elif self.file_list[i].snow_flag and self.summer_file != None:
                return False, str('Select only one snow scan')

        print(self.snow_file)
        print(self.base_file)
        print(self.summer_file)













        #     print(self.file_list[i].check_flags())
        #     flag, msg = self.file_list[i].check_flags()
        #     if not flag:
        #         return msg
            
        #     if self.summer_file == None and msg == 'summer':
        #         self.summer_file = self.file_list[i].file_path
        #     elif self.summer_file != None and msg == 'summer':
        #         return False, str('Select only one summer scan')

        #     if self.base_file == None and msg == 'base':
        #         self.base_file = self.file_list[i].file_path
        #     elif self.base_file != None and msg == 'base':
        #         return False, str('Select only one base scan')

        #     if self.snow_file == None and msg == 'snow':
        #         self.snow_file = self.file_list[i].file_path
        #     elif self.snow_file != None and msg == 'snow':
        #         return False, str('Select only one snow scan')

        # print(self.snow_file)
        # print(self.base_file)
        # print(self.summer_file)

        
            




    def set_snow_file(self):
        #check if snow_file name changed, if so update and flag for files_updated
        pass

    def set_base_file(self):
        #check if base_file name changed, if so update and flag for files_updated
        pass

    def set_summer_file(self):
        #check if summer_file name changed, if so update and flag for files_updated
        pass


