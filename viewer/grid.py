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
        # print('Loaded Files')

    def make_grid(self, cell_size=1):
        self.grid = None

        # Center points about origin
        print('centering points')
        avg_x = []
        avg_y = []
        avg_z = []
        
        for key in self.manager.file_dict:
            if self.manager.file_dict[key] != None:
                avg_x.append(np.mean(self.files[key].init_xyz[:,0]))
                avg_y.append(np.mean(self.files[key].init_xyz[:,1]))
                avg_z.append(np.mean(self.files[key].init_xyz[:,2]))

        self.shift_x = np.mean(avg_x)
        self.shift_y = np.mean(avg_y)
        self.shift_z = np.mean(avg_z)

        print('check extents')
        self.max_x = -float("INF")
        self.min_x = float("INF")
        self.max_y = -float("INF")
        self.min_y = float("INF")
        self.cell_size = cell_size
        for key in self.manager.file_dict:
            print(key)
            if self.manager.file_dict[key] != None:
                self.files[key].shift_points(self.shift_x, self.shift_y, self.shift_z)
                self.files[key].max_x = np.max(self.files[key].xyz[:,0])
                self.files[key].min_x = np.min(self.files[key].xyz[:,0])
                self.files[key].max_y = np.max(self.files[key].xyz[:,1])
                self.files[key].min_y = np.min(self.files[key].xyz[:,1])
                self.files[key].max_z = np.max(self.files[key].xyz[:,2])
                self.files[key].min_z = np.min(self.files[key].xyz[:,2])

                if self.files[key].max_x < self.min_x and self.min_x != float("INF"):
                    print(self.files[key].max_x, self.min_x)
                    print(f"{key} max_x < global min_x. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                if self.files[key].min_x > self.max_x and self.max_x != -float("INF"):
                    print(self.files[key].min_x, self.max_x)
                    print(f"{key} min_x > global max_x. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."

                if self.files[key].max_x > self.max_x:
                    self.max_x = self.files[key].max_x
                if self.files[key].min_x < self.min_x:
                    self.min_x= self.files[key].min_x

                if self.files[key].max_y < self.min_y and self.min_y != float("INF"):
                    print(self.files[key].max_y, self.min_y)
                    print(f"{key} max_y < global min_y. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                if self.files[key].min_y > self.max_y and self.max_y != -float("INF"):
                    print(self.files[key].min_y, self.max_y)
                    print(f"{key} min_y > global max_y. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                
                if self.files[key].max_y > self.max_y:
                    self.max_y = self.files[key].max_y
                if self.files[key].min_y < self.min_y:
                    self.min_y= self.files[key].min_y

        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(self.max_x - self.min_x)
        delta_y = abs(self.max_y - self.min_y)

        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)
        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)

        # print("\nTotal number of grid cells: ", self.number_of_cells_x*self.number_of_cells_y)

        #################################################
        # make grid
        self.grid = [[Grid_Cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]
        
        for key in self.files:
            if self.files[key] != None:
                self.add_points_to_grid(key)

        return f"Grid Complete! {self.number_of_cells_y*self.number_of_cells_x} Total Grid Cells"


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
            # plt.hist(self.snow_depth_array_dict[key], bins = 'auto')
            # plt.title(key)
            # plt.show()

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


    def color_points(self, upper_bound, lower_bound):
        # TODO: Write shading according to the std of the depths make the max 2 stdevs away
        # TODO: Add toggle button for plotting. Color all points each time regardless?
        # TODO: When coloring and calculating snowdepth, if we are basing vegetation off of snow, should the min z value for depth be used in the ground and intermediate scans?
        # TODO: Load in YC summer file, 12/10 and spring file for demonstration
        # TODO: 
        vegetation_color = [0, 65535, 0]
        negative_depth_color = [0, 0, 65535]
        positive_depth_color = [65535, 0, 0]
        if self.snow_depth_key not in ['Ground', 'Inter. Snow']:
            if self.files['New Snow'] != None:
                self.plot_key = 'New Snow'
            elif self.files['Ground'] != None:
                self.plot_key = 'Ground'
            elif self.files['Inter. Snow'] != None:
                self.plot_key = 'Inter. Snow'
            else:
                print('No file selected to plot')
                return 'No file selected to plot'
                
            self.files[self.plot_key].plot_red =  self.files[self.plot_key].red
            self.files[self.plot_key].plot_green =  self.files[self.plot_key].green
            self.files[self.plot_key].plot_blue =  self.files[self.plot_key].blue

            for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict[self.plot_key]:
                            for k in range(len(self.grid[i][j].point_arrays[self.plot_key])):
                                self.files[self.plot_key].plot_red[self.grid[i][j].point_arrays[self.plot_key][k].index] = vegetation_color[0]
                                self.files[self.plot_key].plot_green[self.grid[i][j].point_arrays[self.plot_key][k].index] = vegetation_color[1]
                                self.files[self.plot_key].plot_blue[self.grid[i][j].point_arrays[self.plot_key][k].index] = vegetation_color[2]
            print("Only coloring by vegetation and using default colors.")
            return "Only coloring by vegetation and using default colors."

        else:
            self.plot_key = 'New Snow'
            if upper_bound != '':
                self.upper_bound = float(upper_bound)
            else:
                stdev = np.std(self.snow_depth_array_dict[self.snow_depth_key])
                if (self.average_scan_depth_dict[self.snow_depth_key]+2*stdev) > 0:
                    self.upper_bound = self.average_scan_depth_dict[self.snow_depth_key] + 2*stdev
                else:
                    self.upper_bound = 0

            if lower_bound != '':
                self.lower_bound = float(lower_bound)
            else:
                stdev = np.std(self.snow_depth_array_dict[self.snow_depth_key])
                if (self.average_scan_depth_dict[self.snow_depth_key]-2*stdev) < 0:
                    self.lower_bound = self.average_scan_depth_dict[self.snow_depth_key] - 2*stdev
                else:
                    self.lower_bound = 0

            print('upper bound', self.upper_bound)
            print('lower bound', self.lower_bound)   

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
                            if self.grid[i][j].depth_dict[self.snow_depth_key] <= self.lower_bound:
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[0]
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[1]
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = negative_depth_color[2]
                            else: 
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - self.lower_bound)/(self.lower_bound))*65535 )
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - self.lower_bound)/(self.lower_bound))*65535 )
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = 65535

                        else:
                            if self.grid[i][j].depth_dict[self.snow_depth_key] >= self.upper_bound:
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[0]
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[1]
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = positive_depth_color[2]
                            else: 
                                for k in range(len(self.grid[i][j].point_arrays[key])):
                                    self.files[key].plot_red[self.grid[i][j].point_arrays[key][k].index] = 65535
                                    self.files[key].plot_green[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - self.upper_bound)/(self.upper_bound))*65535 )
                                    self.files[key].plot_blue[self.grid[i][j].point_arrays[key][k].index] = int(abs((self.grid[i][j].depth_dict[self.snow_depth_key] - self.upper_bound)/(self.upper_bound))*65535 )
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

        snow_rgb = np.stack((self.files[self.plot_key].plot_red/max(self.files[self.plot_key].plot_red), self.files[self.plot_key].plot_green/max(self.files[self.plot_key].plot_green), self.files[self.plot_key].plot_blue/max(self.files[self.plot_key].plot_blue)))
        snow_rgb = np.transpose(snow_rgb)

        self.scene = Scene(self, self.files[self.plot_key].xyz, snow_rgb)

        return self.scene

    def get_stats(self, points):
        sum_depth = 0
        count = 0
        max_depth = -float('INF')
        min_depth = float('INF')
        # print('points', len(points))
        for point in points:
            # print(point)
            i = math.floor((point[0]-self.min_x)/self.cell_size)
            j = math.floor((point[1]-self.min_y)/self.cell_size)
            # print(i)
            # print(j)
            # print('snow depth key', self.snow_depth_key)
            # print('cell depth',self.grid[i][j].depth_dict[self.snow_depth_key])
            # print(self.grid[i][j].vegetation_flag_dict['New Snow'])
            if not self.grid[i][j].vegetation_flag_dict['New Snow']:
                # print('here')
                depth = self.grid[i][j].depth_dict[self.snow_depth_key]
                if depth > max_depth:
                    max_depth = depth
                if depth < min_depth:
                    min_depth = depth
                sum_depth += depth
                count +=1
            try:
                average_depth = round(sum_depth/count, 2)
            except:
                average_depth = float('INF')

        return average_depth, round(max_depth, 2), round(min_depth, 2)


        


    