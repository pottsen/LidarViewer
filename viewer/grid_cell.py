import numpy as np
import math
import copy

class Grid_Cell():
    def __init__(self):
        self.base_vegetation_flag = False
        self.snow_vegetation_flag = False
        self.base_intensity_flag = False
        self.snow_intensity_flag = False
        self.base_cliff_flag = False
        self.snow_cliff_flag = False
        self.mid_x = None
        self.mid_y = None
        self.base_array = []
        self.snow_array = []
        self.base_max_z = -float("INF")
        self.base_min_z = float("INF")
        self.base_delta_z = 0
        self.base_total_z = 0
        self.snow_max_z = -float("INF")
        self.snow_min_z = float("INF")
        self.snow_delta_z = 0
        self.snow_total_z = 0
        self.depth = 0

    
    def set_mid_x(self, mid_x):
        self.mid_x = mid_x

    def set_mid_y(self, mid_y):
        self.mid_y = mid_y
    
    def get_mid_x(self):
        return self.mid_x

    def get_mid_y(self):
        return self.mid_y

    def add_base_point(self, point):
        self.base_array.append(point)
        self.base_total_z +=point.z
    
    def add_snow_point(self, point):
        self.snow_array.append(point)
        self.snow_total_z += point.z

    def calculate_average_base_z(self):
        if len(self.base_array) > 0:
            self.base_average_z = self.base_total_z/len(self.base_array)
        else:
            # print("No base points in grid cell")
            pass

    def calculate_average_snow_z(self):
        if len(self.snow_array) > 0:
            self.snow_average_z = self.snow_total_z/len(self.snow_array)
        else:
            # print("No snow points in grid cell")
            pass

    def find_vegetation(self, height, flag):
        ##########################################
        # find max and min z of the cell
        # should I put this in the add_point function?
        if flag == "base":
            self.base_min_z = float("INF")
            self.base_max_z = -float("INF")
            for point in self.base_array:
                if point.z < self.base_min_z:
                    self.base_min_z = point.z
                if point.z > self.base_max_z:
                    self.base_max_z = point.z
            if abs(self.base_max_z - self.base_min_z) > height and abs(self.base_max_z - self.base_min_z) != float("INF"):
                # print("delta z ", abs(self.max_z - self.min_z))
                # print("vegetation found")
                self.base_vegetation_flag = True

        elif flag == "snow":
            self.snow_min_z = float("INF")
            self.snow_max_z = -float("INF")
            for point in self.snow_array:
                if point.z < self.snow_min_z:
                    self.snow_min_z = point.z
                if point.z > self.snow_max_z:
                    self.snow_max_z = point.z
            if abs(self.snow_max_z - self.snow_min_z) > height and abs(self.snow_max_z - self.snow_min_z) != float("INF"):
                # print("delta z ", abs(self.max_z - self.min_z))
                # print("vegetation found")
                self.snow_vegetation_flag = True
