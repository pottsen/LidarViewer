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
import matplotlib.pyplot as plt
from scene import Scene

import vispy.scene
from vispy.scene import visuals

class Grid():
    def __init__(self, manager):
        # TODO: Have user input cell size?
        self.cell_size = 0.5

        # initialize parameters
        self.ground_max_snow_depth = -float("INF")
        self.ground_min_snow_depth = float("INF")
        self.intSnow_max_snow_depth = -float("INF")
        self.intSnow_min_snow_depth = float("INF")
        
        # dictionary of average total depth of the scans
        self.average_scan_depth_dict = {'Ground':0, 'Int. Snow':0}

        # dictionary of an array of the average cell snow depths by scan
        self.snow_depth_array_dict = {'Ground':[], 'Int. Snow':[]}
        
        # store file names of scans in the grid
        self.files = {'Ground': None, 'Int. Snow': None, 'New Snow': None}

        # tie grid to manager
        self.manager = manager

        # key for what scan to pull stats from
        self.stats_key = None

        # initialize values for the upper and lower bounds of the coloring
        self.upper_bound = ''
        self.lower_bound = ''

    # assign file to dictionary of scans in the grid
    def add_data(self, key, las_data):
        self.files[key] = las_data

    # clear all assigned files
    def reset_files(self):
        self.files = {'Ground': None, 'Int. Snow': None, 'New Snow': None}

    def load_files(self, file_dict):
        for key in file_dict:
            if file_dict[key] != None:
                print('Key', key)
                self.files[key] = Grid_File(file_dict[key])
    
    # create the grid
    def make_grid(self, cell_size=0.5):
        # clear previous grid
        self.grid = None

        # initialize extents
        self.max_x = -float("INF")
        self.min_x = float("INF")
        self.max_y = -float("INF")
        self.min_y = float("INF")
        self.cell_size = cell_size

        # go through assigned files and find the extents
        for key, value in self.files.items():
            print(key)
            if value != None:

                value.max_x = np.max(value.xyz[:,0])
                value.min_x = np.min(value.xyz[:,0])
                value.max_y = np.max(value.xyz[:,1])
                value.min_y = np.min(value.xyz[:,1])
                value.max_z = np.max(value.xyz[:,2])
                value.min_z = np.min(value.xyz[:,2])

                delta_x = abs(value.max_x - value.min_x)
                delta_y = abs(value.max_y - value.min_y)
                density = len(value.x)/(delta_x*delta_y)
                print(f'{key} point density(per m2): ', density)

                # Warning Messages
                if value.max_x < self.min_x and self.min_x != float("INF"):
                    print(value.max_x, self.min_x)
                    print(f"{key} max_x < global min_x. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                if value.min_x > self.max_x and self.max_x != -float("INF"):
                    print(value.min_x, self.max_x)
                    print(f"{key} min_x > global max_x. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."

                if value.max_x > self.max_x:
                    self.max_x = value.max_x
                if value.min_x < self.min_x:
                    self.min_x= value.min_x

                if value.max_y < self.min_y and self.min_y != float("INF"):
                    print(value.max_y, self.min_y)
                    print(f"{key} max_y < global min_y. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                if value.min_y > self.max_y and self.max_y != -float("INF"):
                    print(value.min_y, self.max_y)
                    print(f"{key} min_y > global max_y. Scans may not overlap. Check accuracy of coordinates")
                    return f"WARNING: {key} Scan does not overlap with one or all of the other scans! Please check alignment."
                
                if value.max_y > self.max_y:
                    self.max_y = value.max_y
                if value.min_y < self.min_y:
                    self.min_y= value.min_y

        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(self.max_x - self.min_x)
        delta_y = abs(self.max_y - self.min_y)

        # find number of grid cells in X and Y        
        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)
        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)

        #################################################
        # make grid by creating 2D grid cell array
        self.grid = [[Grid_Cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]

        # add points to grid
        for key, value in self.files.items():
            if value != None:
                self.add_points_to_grid(key)


        return f"Grid Complete! {self.number_of_cells_y*self.number_of_cells_x} Total Grid Cells" 



    def add_points_to_grid(self, key):
        #################################################
        # add points to grid cells

        # Get max color values. The color values must be scaled between 0 and 1. This allows us to do that.
        max_red = max(self.files[key].red)
        max_green = max(self.files[key].green)
        max_blue = max(self.files[key].blue)

        for i in range(len(self.files[key].x)):
            if (i % 1000000) == 0:
                print(i, " of ", len(self.files[key].x), f" {key} points added to grid")

            # figure out which grid cell the point goes into. Difference of coordinate and min coordinate of the grid then divided by the grid cell size
            grid_x = math.floor((self.files[key].x[i]-self.min_x)/self.cell_size)
            grid_y = math.floor((self.files[key].y[i]-self.min_y)/self.cell_size)

            # add point to grid cell
            point = Point_Class(i, self.files[key].x[i], self.files[key].y[i], self.files[key].z[i], self.files[key].red[i]/max_red, self.files[key].green[i]/max_green, self.files[key].blue[i]/max_blue, self.files[key].intensity[i])

            self.grid[grid_x][grid_y].add_point(key, point)

            # flag for low intensity
            if self.files[key].intensity[i] < 40000:
                    self.grid[grid_x][grid_y].intensity_flag_dict[key] = True

        print(f"All {key} points added to grid cells.")

    def flag_vegetation(self):
        counts = {}
        point_counts={} #del
        for key, value in self.files.items():
            # make sure a file is assigned to the dictionary key
            if value != None:
                max_points = 0
                veg_count = 0
                point_count = 0
                print(f"Flagging vegetation by {key}...")
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        point_count += len(self.grid[i][j].point_arrays[key])

                        # 60 degrees slope angle equivalent
                        self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, key)
                        
                        if self.grid[i][j].vegetation_flag_dict[key] == True:
                            veg_count += 1
                        
                        if len(self.grid[i][j].point_arrays[key]) > max_points:
                            max_points = len(self.grid[i][j].point_arrays[key])
                point_counts[key] = point_count #del
                counts[key] = veg_count

        print('Point Counts:\n', point_counts) #del
        return counts

    def calculate_snow_depth(self):
        # go through each file in snow depth array dictionary
        for key in self.snow_depth_array_dict.keys():
            if self.files[key] != None:
                self.snow_depth_array_dict[key] = []
                print('Calculating snow depth')
                print(key, self.files[key])
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        # check if vegetation
                        if self.grid[i][j].vegetation_flag_dict['New Snow'] or self.grid[i][j].vegetation_flag_dict[key]:
                            pass

                        else:
                            # calculate average z of ground/intSnow
                            self.grid[i][j].calculate_average_z(key)
                            # calculate average z of newSnow
                            self.grid[i][j].calculate_average_z('New Snow')

                            # make sure points from both scans are present and then calculate depth and append the value to the array dictionary
                            if len(self.grid[i][j].point_arrays['New Snow']) > 0 and len(self.grid[i][j].point_arrays[key]) > 0:
                                self.grid[i][j].depth_dict[key] = self.grid[i][j].average_z_dict['New Snow'] -  self.grid[i][j].average_z_dict[key]
                                
                                self.grid[i][j].min_z_depth_dict[key] = self.grid[i][j].average_z_dict['New Snow'] -  self.grid[i][j].min_z_dict[key]
                        
                                self.snow_depth_array_dict[key].append(self.grid[i][j].depth_dict[key])
                                
                            else:
                                # flag as missing data
                                if len(self.grid[i][j].point_arrays['New Snow']) < 1: 
                                    self.grid[i][j].missing_point_flag_dict['New Snow']= True
                                if len(self.grid[i][j].point_arrays[key]) < 1:
                                    self.grid[i][j].missing_point_flag_dict[key]= True
                
                # plot histogram distribution of snow depths             
                plt.hist(self.snow_depth_array_dict[key], bins = 'auto')
                plt.title(key)
                plt.show()

                # take mean of average depth array to get average depth of whole scan
                self.average_scan_depth_dict[key] = np.mean(self.snow_depth_array_dict[key])

        return self.average_scan_depth_dict #, self.max_snow_depth, self.min_snow_depth

    # get the max and min depths for coloring (uses 2 standard deviations away from the mean)
    def get_max_and_min_depth(self, scan_basis):
        stdev = np.std(self.snow_depth_array_dict[scan_basis])
        if (self.average_scan_depth_dict[scan_basis]-2*stdev) < 0:
            self.min_bound = self.average_scan_depth_dict[scan_basis] - 2*stdev
        else:
            self.min_bound = 0
        if (self.average_scan_depth_dict[scan_basis]+2*stdev) > 0:
            self.max_bound = self.average_scan_depth_dict[scan_basis] + 2*stdev
        else:
            self.max_bound = 0
        return round(self.max_bound, 2), round(self.min_bound, 2)
    
    # get the max and min intensity for coloring
    def get_max_and_min_intensity(self, scan_basis):
        self.max_intensity = max(self.files[scan_basis].intensity)
        self.min_intensity = min(self.files[scan_basis].intensity)
        return self.max_intensity, self.min_intensity

    # reset all the basis info 
    def reset_basis_info(self):
        self.stats_key = None
        self.intensity_key = None
        self.max_bound = None
        self.min_bound = None
        self.max_intensity = None
        self.min_intensity = None
        return '-', '-'

    # calculate and assign coloring values for the points
    def color_points(self, color_basis, scan_basis, upper_bound, lower_bound):
        self.color_basis = color_basis
        # red, green, blue
        vegetation_color = [0, 65535, 0]
        negative_color = [0, 0, 65535]
        positive_color = [65535, 0, 0]
        missing_point_color = [0, 45500, 0]

        # SET DEFAULT IF COLOR BASIS NOT SPECIFIED
        if self.color_basis not in ['intensity', 'depth']:
            self.color_basis = 'default'
            scan_basis = 'default'
            self.upper_bound = 0
            self.lower_bound = 0


        # SET DEFAULT IF SCAN BASIS NOT SPECIFIED
        if scan_basis not in ['Ground', 'Int. Snow', 'New Snow']:
            self.color_basis = 'default'
            if self.files['New Snow'] != None:
                scan_basis = 'New Snow'
            elif self.files['Ground'] != None:
                scan_basis = 'Ground'
            elif self.files['Int. Snow'] != None:
                scan_basis = 'Int. Snow'
            else:
                print('No file selected to plot')
                return 'No file selected to plot'

        #  CHECK TO MAKE SURE SNOW DEPTH HAS BEEN CALCULATED
        if scan_basis in ['Ground', 'Int. Snow'] and self.color_basis in ['depth']:
            if self.snow_depth_array_dict[scan_basis] == []:
                    self.color_basis = 'default'
                    self.upper_bound = 0
                    self.lower_bound = 0
                    # scan_basis = 'default'


        print(self.color_basis)
        # ALWAYS RESET COLORING TO ORIGINAL
        for key in [scan_basis, 'New Snow']:
            if self.files[key] != None:
                self.files[key].plot_red = copy.deepcopy(self.files[key].red)
                self.files[key].plot_blue = copy.deepcopy(self.files[key].blue)
                self.files[key].plot_green = copy.deepcopy(self.files[key].green)

        # 'default' is grey with green vegetation
        if self.color_basis == 'default':
            for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict[scan_basis]:
                            for point in self.grid[i][j].point_arrays[scan_basis]:
                                index = point.index
                                self.files[scan_basis].plot_red[index] = vegetation_color[0]
                                self.files[scan_basis].plot_green[index] = vegetation_color[1]
                                self.files[scan_basis].plot_blue[index] = vegetation_color[2]
            print("Only coloring by vegetation and using default colors.")

        # color based on intensity
        if self.color_basis == 'intensity':
            print(f'Coloring: intensity scan basis {scan_basis}')
            intensities = self.files[scan_basis].intensity
            intensity_stdev = np.std(np.array(intensities))
            intensity_mean = np.mean(np.array(intensities))
            if upper_bound == '':
                self.upper_bound = intensity_mean+intensity_stdev 
            else:
                self.upper_bound = float(upper_bound)
            if lower_bound == '':
                self.lower_bound = intensity_mean-intensity_stdev
            else:
                self.lower_bound = float(lower_bound)
            
            print('upper bound', upper_bound)
            print('lower bound', lower_bound)
            median = (self.upper_bound + self.lower_bound)/2
            print('median intensity', median)

            # scale and assign colors
            for i in range(len(intensities)):
                if intensities[i] < median:
                    if intensities[i] > self.lower_bound:
                        self.files[scan_basis].plot_red[i] = int(abs(intensities[i] - self.lower_bound)/abs(self.lower_bound-median)*65535 )

                        self.files[scan_basis].plot_green[i] = int(abs(intensities[i] - self.lower_bound)/abs(self.lower_bound-median)*65535 )

                        self.files[scan_basis].plot_blue[i] = 65535

                    if intensities[i] <= self.lower_bound:
                        self.files[scan_basis].plot_red[i] = negative_color[0]

                        self.files[scan_basis].plot_green[i] = negative_color[1]

                        self.files[scan_basis].plot_blue[i] = negative_color[2]
                if intensities[i] > median:
                    if intensities[i] < self.upper_bound:
                        self.files[scan_basis].plot_red[i] = 65535

                        self.files[scan_basis].plot_green[i] = int(abs(self.upper_bound - intensities[i])/abs(self.upper_bound-median)*65535 )

                        self.files[scan_basis].plot_blue[i] = int(abs(self.upper_bound - intensities[i])/abs(self.upper_bound-median)*65535 )

                    if intensities[i] >= self.upper_bound:
                        self.files[scan_basis].plot_red[i] = positive_color[0]

                        self.files[scan_basis].plot_green[i] = positive_color[1]

                        self.files[scan_basis].plot_blue[i] = positive_color[2]
        
        # color based on depth
        if self.color_basis == 'depth':
            if upper_bound != '':
                self.upper_bound = float(upper_bound)
            else:
                stdev = np.std(self.snow_depth_array_dict[scan_basis])
                if (self.average_scan_depth_dict[scan_basis]+2*stdev) > 0:
                    self.upper_bound = self.average_scan_depth_dict[scan_basis] + 2*stdev
                else:
                    self.upper_bound = 0

            if lower_bound != '':
                self.lower_bound = float(lower_bound)
            else:
                stdev = np.std(self.snow_depth_array_dict[scan_basis])
                if (self.average_scan_depth_dict[scan_basis]-2*stdev) < 0:
                    self.lower_bound = self.average_scan_depth_dict[scan_basis] - 2*stdev
                else:
                    self.lower_bound = 0

            print('upper bound', self.upper_bound)
            print('lower bound', self.lower_bound)   
            
            # when coloring by depth the points from the 'New Snow' scan are always the ones colored
            print(f'Coloring: depth scan basis {scan_basis}')
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j].vegetation_flag_dict['New Snow']:
                        for point in self.grid[i][j].point_arrays['New Snow']:
                            index = point.index
                            self.files['New Snow'].plot_red[index] = vegetation_color[0]
                            self.files['New Snow'].plot_green[index] = vegetation_color[1]
                            self.files['New Snow'].plot_blue[index] = vegetation_color[2]

                    elif self.grid[i][j].missing_point_flag_dict['New Snow'] or self.grid[i][j].missing_point_flag_dict[scan_basis]:
                        for point in self.grid[i][j].point_arrays['New Snow']:
                            index = point.index
                            self.files['New Snow'].plot_red[index] = missing_point_color[0]
                            self.files['New Snow'].plot_green[index] = missing_point_color[1]
                            self.files['New Snow'].plot_blue[index] = missing_point_color[2]

                    elif self.grid[i][j].depth_dict[scan_basis] < 0:
                        if self.grid[i][j].depth_dict[scan_basis] <= self.lower_bound:
                            for point in self.grid[i][j].point_arrays['New Snow']:
                                index = point.index
                                self.files['New Snow'].plot_red[index] = negative_color[0]
                                self.files['New Snow'].plot_green[index] = negative_color[1]
                                self.files['New Snow'].plot_blue[index] = negative_color[2]
                        else: 
                            for point in self.grid[i][j].point_arrays['New Snow']:
                                index = point.index
                                
                                self.files['New Snow'].plot_red[index] = int(abs((self.grid[i][j].depth_dict[scan_basis] - self.lower_bound)/(self.lower_bound))*65535 )

                                self.files['New Snow'].plot_green[index] = int(abs((self.grid[i][j].depth_dict[scan_basis] - self.lower_bound)/(self.lower_bound))*65535 )

                                self.files['New Snow'].plot_blue[index] = 65535

                    else:
                        if self.grid[i][j].depth_dict[scan_basis] >= self.upper_bound:
                            for point in self.grid[i][j].point_arrays['New Snow']:
                                index = point.index
                                self.files['New Snow'].plot_red[index] = positive_color[0]
                                self.files['New Snow'].plot_green[index] = positive_color[1]
                                self.files['New Snow'].plot_blue[index] = positive_color[2]
                        else: 
                            for point in self.grid[i][j].point_arrays['New Snow']:
                                index = point.index

                                self.files['New Snow'].plot_red[index] = 65535

                                self.files['New Snow'].plot_green[index] = int(abs((self.grid[i][j].depth_dict[scan_basis] - self.upper_bound)/(self.upper_bound))*65535 )

                                self.files['New Snow'].plot_blue[index] = int(abs((self.grid[i][j].depth_dict[scan_basis] - self.upper_bound)/(self.upper_bound))*65535 )
        xyz, rgb = self.get_coordinates_and_scale_color(self.color_basis, scan_basis)
        print('UP', self.upper_bound)
        return xyz, rgb, round(self.upper_bound), round(self.lower_bound)

    def get_coordinates_and_scale_color(self, color_basis, scan_basis):
        self.stats_key = scan_basis
        if self.color_basis in ['default', 'intensity']:
            rgb = np.stack((self.files[scan_basis].plot_red/max(self.files[scan_basis].plot_red), self.files[scan_basis].plot_green/max(self.files[scan_basis].plot_green), self.files[scan_basis].plot_blue/max(self.files[scan_basis].plot_blue)))
            rgb = np.transpose(rgb)
            print(rgb)

            scene = Scene(self, self.files[scan_basis].xyz, rgb, self.color_basis)
            
            return self.files[scan_basis].xyz, rgb

        if self.color_basis == 'depth':
            snow_rgb = np.stack((self.files['New Snow'].plot_red/max(self.files['New Snow'].plot_red), self.files['New Snow'].plot_green/max(self.files['New Snow'].plot_green), self.files['New Snow'].plot_blue/max(self.files['New Snow'].plot_blue)))
            snow_rgb = np.transpose(snow_rgb)
            print(snow_rgb)

            scene = Scene(self, self.files['New Snow'].xyz, snow_rgb, self.color_basis)

            return self.files['New Snow'].xyz, snow_rgb

    # function to pull the depth stats from the plot 
    def get_depth_stats(self, points):
        # points come from the scene class and are the selected points
        sum_depth = 0
        sum_min_z_depth = 0
        count = 0
        max_depth = -float('INF')
        max_min_z_depth = -float('INF')
        min_depth = float('INF')
        for point in points:
            print(point)
            i = math.floor((point[0]-self.min_x)/self.cell_size)
            j = math.floor((point[1]-self.min_y)/self.cell_size)
            
            print('Vegetation NS: ', self.grid[i][j].vegetation_flag_dict['New Snow'])
            print(f'Vegetation {self.stats_key}: ', self.grid[i][j].vegetation_flag_dict[self.stats_key])

            # make sure grid cell is not vegetation or missing points
            if not self.grid[i][j].vegetation_flag_dict['New Snow'] and not self.grid[i][j].missing_point_flag_dict['New Snow'] and not self.grid[i][j].missing_point_flag_dict[self.stats_key]:
                depth = self.grid[i][j].depth_dict[self.stats_key]
                min_z_depth = self.grid[i][j].min_z_depth_dict[self.stats_key]
                print('grid cell:', i, ", ", j, " Depth ", depth)
                if depth > max_depth:
                    max_depth = depth
                if depth < min_depth:
                    min_depth = depth
                if min_z_depth > max_min_z_depth:
                    max_min_z_depth = min_z_depth
                sum_depth += depth
                sum_min_z_depth += min_z_depth
                count +=1
            else:
                print("Vegetation cell")
            try:
                average_depth = round(sum_depth/count, 2)
                average_min_z_depth = round(sum_min_z_depth/count, 2)
            except:
                average_depth = float('INF')
                average_min_z_depth = float('INF')

        return average_depth, round(max_depth, 2), round(min_depth, 2), average_min_z_depth, round(max_min_z_depth, 2)

    # function to pull intenisty stats from the plot
    def get_intensity_stats(self, selected):
        intensities = self.files[self.stats_key].intensity[tuple(selected)]
        average = np.mean(intensities)
        max_intensity = max(intensities)
        min_intensity = min(intensities)
        return round(average,2), round(max_intensity, 2), round(min_intensity, 2)

    # get indices of vegetation points
    def get_vegetation_indices(self):
        indices = []
        for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j].vegetation_flag_dict['New Snow']:
                        for point in self.grid[i][j].point_arrays['New Snow']:
                            indices.append(point.index)
                            

        return indices
    