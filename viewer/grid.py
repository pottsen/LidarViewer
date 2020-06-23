from point import Point_Class
# from canvas_and_window_dock import Canvas
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

import vispy.scene
from vispy.scene import visuals

class Grid():
    def __init__(self):
        # TODO: Have user input cell size?
        # self.cell_size = cell_size
        self.max_snow_depth = -float("INF")
        self.min_snow_depth = float("INF")
        self.average_snow_depth = 0

    def set_grid_to_canvas(self):
        return self

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

    def flag_vegetation(self, flag):
        max_points = 0
        total = 0
        count = 0
        if flag == "base":
            print("Flagging vegetation by base...")
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    total += len(self.grid[i][j].base_array)
                    self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    if self.grid[i][j].base_vegetation_flag == True:
                        count += 1
                    
                    if len(self.grid[i][j].base_array) > max_points:
                        max_points = len(self.grid[i][j].base_array)

        if flag == "snow":
            print("Flagging vegetation by snow...")
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    total += len(self.grid[i][j].snow_array)
                    self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    if self.grid[i][j].snow_vegetation_flag == True:
                        count += 1
                    
                    if len(self.grid[i][j].snow_array) > max_points:
                        max_points = len(self.grid[i][j].snow_array)

        return count, self.number_of_cells_y*self.number_of_cells_x

    def calculate_snow_depth(self):
        snow_depth_array = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].snow_vegetation_flag or self.grid[i][j].base_vegetation_flag:
                    pass
                    # print("vegetation encountered")
                
                # elif self.grid[i][j].snow_intensity_flag or self.grid[i][j].base_intensity_flag:
                #     pass 

                else:
                    self.grid[i][j].calculate_average_base_z()
                    self.grid[i][j].calculate_average_snow_z()
                    if (len(self.grid[i][j].snow_array) > 0 and len(self.grid[i][j].base_array) > 0):
                        self.grid[i][j].depth = self.grid[i][j].snow_average_z -  self.grid[i][j].base_average_z
                        # print(self.grid[i][j].depth)
                    
                        self.average_snow_depth += self.grid[i][j].depth
                        snow_depth_array.append(self.grid[i][j].depth)
                        
                        ## store max and min depths for coloring
                        if self.grid[i][j].depth > self.max_snow_depth:
                            self.max_snow_depth = self.grid[i][j].depth

                        if self.grid[i][j].depth < self.min_snow_depth:
                            self.min_snow_depth = self.grid[i][j].depth
                    else:
                        # print("no snow or base points")
                        pass

        self.average_snow_depth = self.average_snow_depth/(len(self.grid)*len(self.grid[0]))

        # print("Max Depth: ", self.max_snow_depth)
        # print("Min Depth: ", self.min_snow_depth)
        # print("Average Depth: ", self.average_snow_depth)

        return self.average_snow_depth, self.max_snow_depth, self.min_snow_depth

    def color_points(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].snow_vegetation_flag or self.grid[i][j].base_vegetation_flag:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 0
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 0
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 0
                        self.base_green[self.grid[i][j].base_array[k].index] = 65535
                        self.base_blue[self.grid[i][j].base_array[k].index] = 0

                elif self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = int(abs(self.grid[i][j].depth-self.min_snow_depth)/(self.min_snow_depth)*65535 )
                        self.snow_green[self.grid[i][j].snow_array[k].index] = int(abs(self.grid[i][j].depth-self.min_snow_depth)/(self.min_snow_depth)*65535 )
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = int(abs(self.grid[i][j].depth-self.min_snow_depth)/(self.min_snow_depth)*65535 )
                        self.base_green[self.grid[i][j].base_array[k].index] = int(abs(self.grid[i][j].depth-self.min_snow_depth)/(self.min_snow_depth)*65535 )
                        self.base_blue[self.grid[i][j].base_array[k].index] = 65535
                
                elif self.grid[i][j].depth == 0:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 32770
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 32770
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 32770

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 32770
                        self.base_green[self.grid[i][j].base_array[k].index] = 32770
                        self.base_blue[self.grid[i][j].base_array[k].index] = 32770
                
                else:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_green[self.grid[i][j].snow_array[k].index] = int(abs(self.max_snow_depth-self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = int(abs(self.max_snow_depth-self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        self.base_green[self.grid[i][j].base_array[k].index] = int(abs(self.max_snow_depth-self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.base_blue[self.grid[i][j].base_array[k].index] = int(abs(self.max_snow_depth-self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

    def plot_points_initial(self):   
        self.init_canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = self.init_canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = "blue", size = 4)
        view.add(scatter2)

        view.camera = 'arcball' 
        axis = visuals.XYZAxis(parent=view.scene)
        view.add(axis)

        return self.init_canvas
                
    def plot_points(self):   
        base_rgb = np.stack((self.base_red/max(self.base_red), self.base_green/max(self.base_green), self.base_blue/max(self.base_blue)))
        base_rgb = np.transpose(base_rgb)

        snow_rgb = np.stack((self.snow_red/max(self.snow_red), self.snow_green/max(self.snow_green), self.snow_blue/max(self.snow_blue)))
        snow_rgb = np.transpose(snow_rgb)

        self.plot_canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = self.plot_canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 2)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = snow_rgb, size = 2)
        view.add(scatter2)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        axis = visuals.XYZAxis(parent=view.scene)
        view.add(axis)

        return self.plot_canvas
        



    