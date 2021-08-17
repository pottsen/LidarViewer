from laspy.file import File
import numpy as np
from remove_duplicates import remove_duplicates
import copy

class Las_Data:
    # def __init__(self, flag, file_path):
    def __init__(self, file_path):

        ### Remove Duplicates If Needed
        cleaned_file = remove_duplicates(str(file_path))
        self.file = File(cleaned_file, mode = "r")

        # pull all pertinent data from the las file
        self.file =  File(file_path, mode = "r")
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1]
        self.file_name = self.file_name.split('.')[0]

        # store initial x,y,z coordinates for reference
        self.init_x = self.file.x 
        self.init_y = self.file.y 
        self.init_z = self.file.z 
        self.init_xyz = np.transpose(np.stack((self.init_x, self.init_y, self.init_z)))

        # store x,y,z coordinates for manipulation
        self.x = self.file.x 
        self.y = self.file.y 
        self.z = self.file.z 
        self.xyz = np.transpose(np.stack((self.x, self.y, self.z)))

        # initialize rgb variables for plotting
        self.plot_red = []
        self.plot_blue = []
        self.plot_green = []

        # store intensity values
        self.intensity = self.file.intensity

        # store raw points data
        self.points = self.file.points

        # sometimes RGB is missing
        try:
            self.red = copy.deepcopy(self.file.red)
            self.green = copy.deepcopy(self.file.green)
            self.blue = copy.deepcopy(self.file.blue)
        except:
            self.red = np.ones(len(self.file.points)) * 65535
            self.green = np.ones(len(self.file.points)) * 65535
            self.blue = np.ones(len(self.file.points)) * 65535
        
        self.intensity = copy.deepcopy(self.file.intensity)
    
    # old function probably not needed anymore
    def shift_points(self, shift_x, shift_y, shift_z):
        self.x = self.file.x - shift_x
        self.y = self.file.y - shift_y
        self.z = self.file.z - shift_z
        self.xyz = np.transpose(np.stack((self.x, self.y, self.z)))

    # remove the cropped points specified from the Cropping window
    # init_xyz tracks cropping changes
    def remove_cropped_points(self, selected):
        self.init_x = self.init_x[tuple(np.invert(selected))]
        self.init_y = self.init_y[tuple(np.invert(selected))]
        self.init_z = self.init_z[tuple(np.invert(selected))]
        self.init_xyz = self.init_xyz[tuple(np.invert(selected))]
        self.x = self.x[tuple(np.invert(selected))]
        self.y = self.y[tuple(np.invert(selected))]
        self.z = self.z[tuple(np.invert(selected))]
        self.xyz = self.xyz[tuple(np.invert(selected))]
        self.intensity = self.intensity[tuple(np.invert(selected))]
        self.points = self.points[tuple(np.invert(selected))]
        self.red = self.red[tuple(np.invert(selected))]
        self.green = self.green[tuple(np.invert(selected))]
        self.blue = self.blue[tuple(np.invert(selected))]

    # update points after aligned in Alignment window
    # init_xyz keeps original with cropping changes
    def update_aligned_points(self, points):
        # self.init_x = points[:,0]
        # self.init_y = points[:,1]
        # self.init_z = points[:,2]
        # self.init_xyz = np.transpose(np.stack((self.init_x, self.init_y, self.init_z)))
        self.x = points[:,0]
        self.y = points[:,1]
        self.z = points[:,2]
        self.xyz = np.transpose(np.stack((self.x, self.y, self.z)))

    # reverts back to original alignent with cropped points
    def reset_aligned_points(self):
        self.x = copy.deepcopy(self.init_x)
        self.y = copy.deepcopy(self.init_y)
        self.z = copy.deepcopy(self.init_z)
        self.xyz = np.transpose(np.stack((self.x, self.y, self.z)))
