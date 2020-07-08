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
from grid_file import Grid_File

class Grid():
    def __init__(self, manager):
        # TODO: Have user input cell size?
        # self.cell_size = cell_size
        self.ground_max_snow_depth = -float("INF")
        self.ground_min_snow_depth = float("INF")
        self.intSnow_max_snow_depth = -float("INF")
        self.intSnow_min_snow_depth = float("INF")
        self.average_scan_depth_dict = {'Ground':0, 'Inter. Snow':0}
        self.files = {}
        self.manager = manager

    # def set_grid_to_manager(self):
    #     return self

    def load_files(self, file_dict):
        for key in file_dict:
            if file_dict[key] != None:
                self.files[key] = Grid_File(key, file_dict[key])
        print('Loaded Files')

    def make_grid(self, cell_size=1):
        max_x = -float("INF")
        min_x = float("INF")
        max_y = -float("INF")
        min_y = float("INF")
        self.cell_size = cell_size
        for key in self.manager.file_dict:
            if self.files[key] != None:
                self.files[key].max_x = np.max(self.files[key].xyz[:,0])
                self.files[key].min_x = np.min(self.files[key].xyz[:,0])
                self.files[key].max_y = np.max(self.files[key].xyz[:,1])
                self.files[key].min_y = np.min(self.files[key].xyz[:,1])
                self.files[key].max_z = np.max(self.files[key].xyz[:,2])
                self.files[key].min_z = np.min(self.files[key].xyz[:,2])

                if self.files[key].max_x > max_x:
                    max_x = self.files[key].max_x
                if self.files[key].min_x < min_x:
                    min_x= self.files[key].min_x
                if self.files[key].max_y > max_y:
                    max_y = self.files[key].max_y
                if self.files[key].min_y < min_y:
                    min_y= self.files[key].min_y

        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(max_x - min_x)
        delta_y = abs(max_y - min_y)

        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)
        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)

        print("\nTotal number of grid cells: ", self.number_of_cells_x*self.number_of_cells_y)

        #################################################
        # make grid
        self.grid = [[Grid_Cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]
        
        for key in self.files:
            if self.files[key] != None:
                self.add_points_to_grid(key)

        return self.number_of_cells_y*self.number_of_cells_x


    def add_points_to_grid(self, key):
        #################################################
        # add points to grid cells
        max_red = max(self.files[key].red)
        max_green = max(self.files[key].green)
        max_blue = max(self.files[key].blue)

        for i in range(len(self.files[key].x)):
            if (i % 1000000) == 0:
                print(i, " of ", len(self.files[key].x), f" {key} points added to grid")


            grid_x = math.floor((self.files[key].x[i]-self.files[key].min_x)/self.cell_size)
            grid_y = math.floor((self.files[key].y[i]-self.files[key].min_y)/self.cell_size)
            point = Point_Class(i, self.files[key].x[i], self.files[key].y[i], self.files[key].z[i], self.files[key].red[i]/max_red, self.files[key].green[i]/max_green, self.files[key].blue[i]/max_blue, self.files[key].intensity[i])
            self.grid[grid_x][grid_y].add_point(key, point)

            if self.files[key].intensity[i] < 40000:
                    self.grid[grid_x][grid_y].intensity_flag_dict[key] = True

        print(f"All {key} points added to grid cells.")

    def flag_vegetation(self):
        counts = {}
        for key in self.files:
            if self.files[key] != None:
                max_points = 0
                total = 0
                count = 0
                print(f"Flagging vegetation by {key}...")
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        total += len(self.grid[i][j].point_arrays[key])
                        self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, key)
                        if self.grid[i][j].vegetation_flag_dict[key] == True:
                            count += 1
                        
                        if len(self.grid[i][j].point_arrays[key]) > max_points:
                            max_points = len(self.grid[i][j].point_arrays[key])
                counts[key] = count
        return counts

    def calculate_snow_depth(self):
        self.snow_depth_array_dict = {'Ground':[], 'Inter. Snow':[]}
        for key in self.snow_depth_array_dict:
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j].vegetation_flag_dict['New Snow'] or self.grid[i][j].vegetation_flag_dict[key]:
                        pass
                    # elif self.grid[i][j].snow_intensity_flag or self.grid[i][j].base_intensity_flag:
                    #     pass 

                    else:
                        self.grid[i][j].calculate_average_z(key)
                        self.grid[i][j].calculate_average_z('New Snow')
                        if len(self.grid[i][j].point_arrays['New Snow']) > 0 and len(self.grid[i][j].point_arrays[key]) > 0:
                            self.grid[i][j].depth_dict[key] = self.grid[i][j].average_z_dict['New Snow'] -  self.grid[i][j].average_z_dict[key]
                            # print(self.grid[i][j].depth)
                        
                            self.average_scan_depth_dict[key] += self.grid[i][j].depth_dict[key]
                            self.snow_depth_array_dict[key].append(self.grid[i][j].depth_dict[key])
                            
                            # ## store max and min depths for coloring
                            # if self.grid[i][j].depth > self.max_snow_depth:
                            #     self.max_snow_depth = self.grid[i][j].depth

                            # if self.grid[i][j].depth < self.min_snow_depth:
                            #     self.min_snow_depth = self.grid[i][j].depth
                        else:
                            # print("no snow or base points")
                            pass

            self.average_scan_depth_dict[key] = self.average_scan_depth_dict[key]/(len(self.grid)*len(self.grid[0]))

            # print("Max Depth: ", self.max_snow_depth)
            # print("Min Depth: ", self.min_snow_depth)
            # print("Average Depth: ", self.average_snow_depth)

            return self.average_scan_depth_dict #, self.max_snow_depth, self.min_snow_depth

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
        

# file_dict = {
#     'summer': 'summer',
#     'base': 'base'
# }

# grid = Grid()
# grid.load_files(file_dict)


    