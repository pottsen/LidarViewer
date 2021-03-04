import numpy as np
import math
import copy

class Grid_Cell():
    def __init__(self):
        self.vegetation_flag_dict = {'Ground':False, 'Int. Snow':False, 'New Snow':False}
        self.intensity_flag_dict = {'Ground':False, 'Int. Snow':False, 'New Snow':False}
        self.missing_point_flag_dict = {'Ground':False, 'Int. Snow':False, 'New Snow':False}
        self.cliff_flag_dict = {'Ground':False, 'Int. Snow':False, 'New Snow':False}
        self.mid_x = None
        self.mid_y = None
        self.point_arrays = {'Ground':[], 'Int. Snow':[], 'New Snow':[]}
        self.total_z_dict = {'Ground':0, 'Int. Snow':0, 'New Snow':0}
        self.max_z_dict = {'Ground':-float("INF"), 'Int. Snow':-float("INF"), 'New Snow':-float("INF")}
        self.min_z_dict = {'Ground':float("INF"), 'Int. Snow':float("INF"), 'New Snow':float("INF")}
        self.average_z_dict = {'Ground':0, 'Int. Snow':0, 'New Snow':0}
        self.base_delta_z = 0
        self.snow_delta_z = 0
        self.depth_dict = {'Ground':0, 'Int. Snow':0}
        self.max_depth = 0
        self.ground_depth = 0

    
    def set_mid_x(self, mid_x):
        self.mid_x = mid_x

    def set_mid_y(self, mid_y):
        self.mid_y = mid_y
    
    def get_mid_x(self):
        return self.mid_x

    def get_mid_y(self):
        return self.mid_y

    def add_point(self, key, point):
        self.point_arrays[key].append(point)
        self.total_z_dict[key] +=point.z

    def calculate_average_z(self, key):
        if len(self.point_arrays[key]) > 0:
            self.average_z_dict[key] = self.total_z_dict[key]/len(self.point_arrays[key])

        if key == 'New Snow':
            self.ground_depth = self.average_z_dict['New Snow'] - self.min_z_dict['Ground']

    def find_vegetation(self, height, key):
        ##########################################
        # find max and min z of the cell and check the difference
        for point in self.point_arrays[key]:
            if point.z < self.min_z_dict[key]:
                self.min_z_dict[key] = point.z
            if point.z > self.max_z_dict[key]:
                self.max_z_dict[key] = point.z
        if abs(self.max_z_dict[key] - self.min_z_dict[key]) > height and abs(self.max_z_dict[key] - self.min_z_dict[key]) != float("INF"):
            self.vegetation_flag_dict[key] = True

        if key == 'New Snow':
            self.max_depth = self.max_z_dict['New Snow'] - self.min_z_dict['Ground']

