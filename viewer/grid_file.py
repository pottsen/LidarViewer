from laspy.file import File
import numpy as np
from remove_duplicates import remove_duplicates
import copy

class Grid_File:
    def __init__(self, flag, file_path):
        self.flag = flag
        cleaned_file = remove_duplicates(str(file_path))
        self.file = File(cleaned_file, mode = "r")
        self.file_name = file_path.split('/')[-1]
        self.file_name = self.file_name.split('.')[0]
        self.init_x = self.file.x 
        self.init_y = self.file.y 
        self.init_z = self.file.z 
        self.init_xyz = np.transpose(np.stack((self.init_x, self.init_y, self.init_z)))
        self.x = self.file.x 
        self.y = self.file.y 
        self.z = self.file.z 
        self.xyz = np.transpose(np.stack((self.init_x, self.init_y, self.init_z)))
        self.plot_red = []
        self.plot_blue = []
        self.plot_green = []

        try:
            self.red = copy.deepcopy(self.file.red)
            self.green = copy.deepcopy(self.file.green)
            self.blue = copy.deepcopy(self.file.blue)
        except:
            self.red = np.ones(len(self.file.points)) * 65535
            self.green = np.ones(len(self.file.points)) * 65535
            self.blue = np.ones(len(self.file.points)) * 65535
        
        self.intensity = copy.deepcopy(self.file.intensity)
    
    def shift_points(self, shift_x, shift_y, shift_z):
        self.x = self.file.x - shift_x
        self.y = self.file.y - shift_y
        self.z = self.file.z - shift_z
        self.xyz = np.transpose(np.stack((self.x, self.y, self.z)))

