from point import Point_Class

from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys
import math
import copy
from remove_duplicates import remove_duplicates
from grid_cell import Grid_Cell
# from iterative_closest_point_clean import *

class Grid():
    def __init__(self):
        pass

    def load_base_file(self, base_file_path):
        cleaned_base_file = remove_duplicates(str(base_file_path))
        self.base_file = File(cleaned_base_file, mode = "r")
        self.base_file_name = base_file_path.split('/')[-1]
        self.base_file_name = self.base_file_name.split('.')[0]
        self.base_x = self.base_file.x
        self.base_y = self.base_file.y
        self.base_z = self.base_file.z 
        self.base_xyz = np.stack((self.base_x, self.base_y, self.base_z))
        self.base_xyz = np.transpose(self.base_xyz)
        try:
            self.base_red = copy.deepcopy(self.base_file.red)
            self.base_green = copy.deepcopy(self.base_file.green)
            self.base_blue = copy.deepcopy(self.base_file.blue)
        except:
            self.base_red = np.ones(len(self.base_file.points)) * 65535
            self.base_green = np.ones(len(self.base_file.points)) * 65535
            self.base_blue = np.ones(len(self.base_file.points)) * 65535
        
        self.base_intensity = copy.deepcopy(self.base_file.intensity)

    def load_snow_file(self, snow_file_path):
        cleaned_snow_file = remove_duplicates(str(snow_file_path))
        self.snow_file = File(cleaned_snow_file, mode = "r")
        self.snow_file_name = snow_file_path.split('/')[-1]
        self.snow_file_name = self.snow_file_name.split('.')[0]
        self.snow_x = self.snow_file.x
        self.snow_y = self.snow_file.y
        self.snow_z = self.snow_file.z 
        self.snow_xyz = np.stack((self.snow_x, self.snow_y, self.snow_z))
        self.snow_xyz = np.transpose(self.snow_xyz)
        try:
            self.snow_red = copy.deepcopy(self.snow_file.red)
            self.snow_green = copy.deepcopy(self.snow_file.green)
            self.snow_blue = copy.deepcopy(self.snow_file.blue)
        except:
            self.snow_red = np.ones(len(self.snow_file.points)) * 65535
            self.snow_green = np.ones(len(self.snow_file.points)) * 65535
            self.snow_blue = np.ones(len(self.snow_file.points)) * 65535

        self.snow_intensity = copy.deepcopy(self.snow_file.intensity)

    def make_grid_by_cell(self, cell_size=1):
        self.cell_size = cell_size
        self.base_max_x = np.max(self.base_xyz[:,0])
        self.base_min_x = np.min(self.base_xyz[:,0])
        print("\nmax x", self.base_max_x, "\nmin x", self.base_min_x)

        if round(self.base_max_x,2) != round(self.base_file.header.max[0], 2):
            print("x max coordinate mismatch")
            print("max x of points ", round(self.base_max_x,2))
            print("max x ", round(self.base_file.header.max[0], 2))
    
        if round(self.base_min_x,2) != round(self.base_file.header.min[0], 2):
            print("x min coordinate mismatch")
            print("min x of points ", round(self.base_min_x,2))
            print("min x ", round(self.base_file.header.min[0], 2))

        self.base_max_y = np.max(self.base_xyz[:,1])
        self.base_min_y = np.min(self.base_xyz[:,1])
        print("\nmax y", self.base_max_y, "\nmin y", self.base_min_y)

        if round(self.base_max_y,2) != round(self.base_file.header.max[1], 2):
            print("y max coordinate mismatch")
            print("max y of points ", round(self.base_max_y,2))
            print("max y ", round(self.base_file.header.max[1], 2))
        
        if round(self.base_min_y,2) != round(self.base_file.header.min[1], 2):
            print("y min coordinate mismatch")
            print("min y of points ", round(self.base_min_y,2))
            print("min y ", round(self.base_file.header.min[1], 2))

        self.base_max_z = np.max(self.base_xyz[:,2])
        self.base_min_z = np.min(self.base_xyz[:,2])
        print("\nmax z", self.base_max_z, "\nmin z", self.base_min_z)

        if round(self.base_max_z,2) != round(self.base_file.header.max[2], 2):
            print("z max coordinate mismatch")
            print("max z of points ", round(self.base_max_z,2))
            print("max z ", round(self.base_file.header.max[2], 2))

        if round(self.base_min_z,2) != round(self.base_file.header.min[2], 2):
            print("z min coordinate mismatch")
            print("min z of points ", round(self.base_min_z,2))
            print("min z ", round(self.base_file.header.min[2], 2))

        #### SNOW Data
        self.snow_max_x = np.max(self.snow_xyz[:,0])
        self.snow_min_x = np.min(self.snow_xyz[:,0])
        print("\nmax x", self.snow_max_x, "\nmin x", self.snow_min_x)

        if round(self.snow_max_x,2) != round(self.snow_file.header.max[0], 2):
            print("x max coordinate mismatch")
            print("max x of points ", round(self.snow_max_x,2))
            print("max x ", round(self.snow_file.header.max[0], 2))
    
        if round(self.snow_min_x,2) != round(self.snow_file.header.min[0], 2):
            print("x min coordinate mismatch")
            print("min x of points ", round(self.snow_min_x,2))
            print("min x ", round(self.snow_file.header.min[0], 2))

        self.snow_max_y = np.max(self.snow_xyz[:,1])
        self.snow_min_y = np.min(self.snow_xyz[:,1])
        print("\nmax y", self.snow_max_y, "\nmin y", self.snow_min_y)

        if round(self.snow_max_y,2) != round(self.snow_file.header.max[1], 2):
            print("y max coordinate mismatch")
            print("max y of points ", round(self.snow_max_y,2))
            print("max y ", round(self.snow_file.header.max[1], 2))
        
        if round(self.snow_min_y,2) != round(self.snow_file.header.min[1], 2):
            print("y min coordinate mismatch")
            print("min y of points ", round(self.snow_min_y,2))
            print("min y ", round(self.snow_file.header.min[1], 2))

        self.snow_max_z = np.max(self.snow_xyz[:,2])
        self.snow_min_z = np.min(self.snow_xyz[:,2])
        print("\nmax z", self.snow_max_z, "\nmin z", self.snow_min_z)

        if round(self.snow_max_z,2) != round(self.snow_file.header.max[2], 2):
            print("z max coordinate mismatch")
            print("max z of points ", round(self.snow_max_z,2))
            print("max z ", round(self.snow_file.header.max[2], 2))

        if round(self.snow_min_z,2) != round(self.snow_file.header.min[2], 2):
            print("z min coordinate mismatch")
            print("min z of points ", round(self.snow_min_z,2))
            print("min z ", round(self.snow_file.header.min[2], 2))
        
        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        self.max_x = max(self.base_max_x, self.snow_max_x)
        self.min_x = min(self.base_min_x, self.snow_min_x)

        self.max_y = max(self.base_max_y, self.snow_max_y)
        self.min_y = min(self.base_min_y, self.snow_min_y)

        delta_x = abs(self.max_x - self.min_x)
        delta_y = abs(self.max_y - self.min_y)
        area = float(delta_x)*float(delta_y)

        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)

        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)

        print("\nTotal number of grid cells: ", self.number_of_cells_x*self.number_of_cells_y)


        #################################################
        # make grid
        self.grid = [[Grid_Cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]
        print("\nGrid complete")
        self.add_points_to_grid("base")
        self.add_points_to_grid("snow")

    def add_points_to_grid(self, flag):
        #################################################
        # add points to grid cells
        if flag == "base":
            max_red = max(self.base_red)
            max_green = max(self.base_green)
            max_blue = max(self.base_blue)

            for i in range(len(self.base_file.points)):
                if (i % 1000000) == 0:
                    print(i, " of ", len(self.base_file.points), " base points added to grid")


                grid_x = math.floor((self.base_x[i]-self.min_x)/self.cell_size)
                grid_y = math.floor((self.base_y[i]-self.min_y)/self.cell_size)
                # try:
                point = Point_Class(i, self.base_x[i], self.base_y[i], self.base_z[i], self.base_red[i]/max_red, self.base_green[i]/max_green, self.base_blue[i]/max_blue, self.base_intensity[i])
                self.grid[grid_x][grid_y].add_base_point(point)

                if self.base_intensity[i] < 40000:
                        self.grid[grid_x][grid_y].base_intensity_flag = True

            print("All base points added to grid cells.")

        elif flag == "snow":
            max_red = max(self.snow_red)
            max_green = max(self.snow_green)
            max_blue = max(self.snow_blue)

            for i in range(len(self.snow_file.points)):
                if self.snow_x[i] > self.max_x or self.snow_x[i] < self.min_x or self.snow_y[i] > self.max_y or self.snow_y[i] < self.min_y:
                    print("Snow point out of grid range")
                else:
                    if (i % 1000000) == 0:
                        print(i, " of ", len(self.snow_file.points), " snow points added to grid")
                    grid_x = math.floor((self.snow_x[i]-self.min_x)/self.cell_size)
                    grid_y = math.floor((self.snow_y[i]-self.min_y)/self.cell_size)
                    # try:
                    point = Point_Class(i, self.snow_x[i], self.snow_y[i], self.snow_z[i], self.snow_red[i]/max_red, self.snow_green[i]/max_green, self.snow_blue[i]/max_blue, self.snow_intensity[i])
                    self.grid[grid_x][grid_y].add_snow_point(point)
                    if self.snow_intensity[i] < 40000:
                        self.grid[grid_x][grid_y].snow_intensity_flag = True

            print("All snow points added to grid cells.")



    