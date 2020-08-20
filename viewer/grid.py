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
import matplotlib.pyplot as plt
# from iterative_closest_point_clean import *
from scene import Scene

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
        self.snow_depth_array_dict = {'Ground':[], 'Inter. Snow':[]}
        self.files = {'Ground': None, 'Inter. Snow': None, 'New Snow': None}
        self.manager = manager
        self.snow_depth_key = None

    # def set_grid_to_manager(self):
    #     return self

    def load_files(self, file_dict):
        for key in file_dict:
            if file_dict[key] != None:
                print('Key', key)
                self.files[key] = Grid_File(key, file_dict[key])
        print('Loaded Files')

    def make_grid(self, cell_size=1):
        self.grid = None
        max_x = -float("INF")
        min_x = float("INF")
        max_y = -float("INF")
        min_y = float("INF")
        self.cell_size = cell_size
        for key in self.manager.file_dict:
            if self.manager.file_dict[key] != None:
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
        for key in self.snow_depth_array_dict:
            self.snow_depth_array_dict[key] = []
            print('Calculating snow depth')
            print(key, self.files[key])
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
            plt.hist(self.snow_depth_array_dict[key], bins = 'auto')
            plt.title(key)
            plt.show()

            self.average_scan_depth_dict[key] = self.average_scan_depth_dict[key]/(len(self.grid)*len(self.grid[0]))

            # print("Max Depth: ", self.max_snow_depth)
            # print("Min Depth: ", self.min_snow_depth)
            # print("Average Depth: ", self.average_snow_depth)

        return self.average_scan_depth_dict #, self.max_snow_depth, self.min_snow_depth

    def get_max_and_min_depth(self):
        if self.snow_depth_array_dict[self.snow_depth_key] != []:
            stdev = np.std(self.snow_depth_array_dict[self.snow_depth_key])
            if (self.average_scan_depth_dict[self.snow_depth_key]-2*stdev) < 0:
                self.min_bound = self.average_scan_depth_dict[self.snow_depth_key] - 2*stdev
            else:
                self.min_bound = 0
            if (self.average_scan_depth_dict[self.snow_depth_key]+2*stdev) > 0:
                self.max_bound = self.average_scan_depth_dict[self.snow_depth_key] + 2*stdev
            else:
                self.max_bound = 0
            return round(self.max_bound, 2), round(self.min_bound, 2)
        else:
            return '-', '-'


    def color_points(self):
        # TODO: Write shading according to the std of the depths make the max 2 stdevs away
        # TODO: Add toggle button for plotting. Color all points each time regardless?
        # TODO: When coloring and calculating snowdepth, if we are basing vegetation off of snow, should the min z value for depth be used in the ground and intermediate scans?
        # TODO: Load in YC summer file, 12/10 and spring file for demonstration
        # TODO: 
        vegetation_color = [0, 65535, 0]
        negative_depth_color = [0, 0, 65535]
        positive_depth_color = [65535, 0, 0]
        if self.files[self.snow_depth_key] == None:
            self.files['New Snow'].plot_red =  self.files['New Snow'].red
            self.files['New Snow'].plot_green =  self.files['New Snow'].green
            self.files['New Snow'].plot_blue =  self.files['New Snow'].blue

            for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict['New Snow']:
                            for k in range(len(self.grid[i][j].point_arrays['New Snow'])):
                                self.files['New Snow'].plot_red[self.grid[i][j].point_arrays['New Snow'][k].index] = vegetation_color[0]
                                self.files['New Snow'].plot_green[self.grid[i][j].point_arrays['New Snow'][k].index] = vegetation_color[1]
                                self.files['New Snow'].plot_blue[self.grid[i][j].point_arrays['New Snow'][k].index] = vegetation_color[2]

            return "Only one file loaded. Only coloring by vegetation and using default colors."

        else:
            stdev = np.std(self.snow_depth_array_dict[self.snow_depth_key])
            if (self.average_scan_depth_dict[self.snow_depth_key]-2*stdev) < 0:
                lower_bound = self.average_scan_depth_dict[self.snow_depth_key] - 2*stdev
            else:
                lower_bound = 0
            if (self.average_scan_depth_dict[self.snow_depth_key]+2*stdev) > 0:
                upper_bound = self.average_scan_depth_dict[self.snow_depth_key] + 2*stdev
            else:
                upper_bound = 0

            for key in [self.snow_depth_key, 'New Snow']:
                self.files[key].plot_red = self.files[key].red
                self.files[key].plot_blue = self.files[key].blue
                self.files[key].plot_green = self.files[key].green
            
            for key in ['New Snow']:
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict[key]:
                            for k in range(len(self.grid[i][j].point_arrays[key])):
                                self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = vegetation_color[0]
                                self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = vegetation_color[1]
                                self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = vegetation_color[2]

                        elif self.grid[i][j].depth_dict[self.snow_depth_key] < 0:
                            if self.grid[i][j].depth_dict[self.snow_depth_key] <= lower_bound:
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[0]
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[1]
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[2]
                            else: 
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - lower_bound)/(lower_bound))*65535 )
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - lower_bound)/(lower_bound))*65535 )
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = 65535

                        else:
                            if self.grid[i][j].depth_dict[self.snow_depth_key] >= upper_bound:
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[0]
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[1]
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[2]
                            else: 
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = 65535
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - upper_bound)/(upper_bound))*65535 )
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - upper_bound)/(upper_bound))*65535 )
                return "Points colored by snowdepth."

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
        # base_rgb = np.stack((self.files[self.snow_depth_key].plot_red/max(self.files[self.snow_depth_key].plot_red), self.files[self.snow_depth_key].plot_green/max(self.files[self.snow_depth_key].plot_green), self.files[self.snow_depth_key].plot_blue/max(self.files[self.snow_depth_key].plot_blue)))
        # base_rgb = np.transpose(base_rgb)

        snow_rgb = np.stack((self.files['New Snow'].plot_red/max(self.files['New Snow'].plot_red), self.files['New Snow'].plot_green/max(self.files['New Snow'].plot_green), self.files['New Snow'].plot_blue/max(self.files['New Snow'].plot_blue)))
        snow_rgb = np.transpose(snow_rgb)

        self.scene = Scene(self, self.files['New Snow'].xyz, snow_rgb)

        # self.plot_canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        # view = self.plot_canvas.central_widget.add_view()

        # # scatter = visuals.Markers()
        # # scatter.set_data(self.files[self.snow_depth_key].xyz, edge_color = None, face_color = base_rgb, size = 2)
        # # view.add(scatter)
        
        # scatter2 = visuals.Markers()
        # scatter2.set_data(self.files['New Snow'].xyz, edge_color = None, face_color = snow_rgb, size = 2)
        # view.add(scatter2)
        
        # view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # axis = visuals.XYZAxis(parent=view.scene)
        # view.add(axis)

        return self.scene
        


    