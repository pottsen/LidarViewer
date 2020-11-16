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
        self.average_scan_depth_dict = {'Ground':0, 'Int. Snow':0}
        self.snow_depth_array_dict = {'Ground':[], 'Int. Snow':[]}
        self.files = {'Ground': None, 'Int. Snow': None, 'New Snow': None}
        self.manager = manager
        self.stats_key = None
        self.upper_bound = ''
        self.lower_bound = ''

    # def set_grid_to_manager(self):
    #     return self

    def add_data(self, key, las_data):
        self.files[key] = las_data

    def reset_files(self):
        self.files = {'Ground': None, 'Int. Snow': None, 'New Snow': None}

    def load_files(self, file_dict):
        for key in file_dict:
            if file_dict[key] != None:
                print('Key', key)
                # self.files[key] = Grid_File(key, file_dict[key])
                self.files[key] = Grid_File(file_dict[key])
        # print('Loaded Files')

    def make_grid(self, cell_size=1):
        self.grid = None

        # Center points about origin
        # print('centering points')
        # avg_x = []
        # avg_y = []
        # avg_z = []
        
        # for key in self.manager.file_dict:
        #     if self.manager.file_dict[key] != None:
        #         avg_x.append(np.mean(self.files[key].init_xyz[:,0]))
        #         avg_y.append(np.mean(self.files[key].init_xyz[:,1]))
        #         avg_z.append(np.mean(self.files[key].init_xyz[:,2]))

        # self.shift_x = np.mean(avg_x) #0
        # self.shift_y = np.mean(avg_y) #0
        # self.shift_z = np.mean(avg_z) #0

        print('check extents')
        self.max_x = -float("INF")
        self.min_x = float("INF")
        self.max_y = -float("INF")
        self.min_y = float("INF")
        self.cell_size = cell_size
        for key, value in self.files.items():
            print(key)
            if value != None:
                # print('shifting scan: ', key)
                # self.files[key].shift_points(self.shift_x, self.shift_y, self.shift_z)
                value.max_x = np.max(value.xyz[:,0])
                value.min_x = np.min(value.xyz[:,0])
                value.max_y = np.max(value.xyz[:,1])
                value.min_y = np.min(value.xyz[:,1])
                value.max_z = np.max(value.xyz[:,2])
                value.min_z = np.min(value.xyz[:,2])

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

        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)
        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)

        #################################################
        # make grid
        self.grid = [[Grid_Cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]
        
        for key, value in self.files.items():
            if value != None:
                print(f'{key} point density(per m2): ', len(value.x)/(delta_x*delta_y))
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

            grid_x = math.floor((self.files[key].x[i]-self.min_x)/self.cell_size)
            grid_y = math.floor((self.files[key].y[i]-self.min_y)/self.cell_size)

            point = Point_Class(i, self.files[key].x[i], self.files[key].y[i], self.files[key].z[i], self.files[key].red[i]/max_red, self.files[key].green[i]/max_green, self.files[key].blue[i]/max_blue, self.files[key].intensity[i])
            self.grid[grid_x][grid_y].add_point(key, point)

            if self.files[key].intensity[i] < 40000:
                    self.grid[grid_x][grid_y].intensity_flag_dict[key] = True

        print(f"All {key} points added to grid cells.")

    def flag_vegetation(self):
        counts = {}
        point_counts={}
        for key, value in self.files.items():
            
            if value != None:
                max_points = 0
                veg_count = 0
                point_count = 0
                print(f"Flagging vegetation by {key}...")
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        point_count += len(self.grid[i][j].point_arrays[key])
                        self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, key)
                        if self.grid[i][j].vegetation_flag_dict[key] == True:
                            veg_count += 1
                        
                        if len(self.grid[i][j].point_arrays[key]) > max_points:
                            max_points = len(self.grid[i][j].point_arrays[key])
                point_counts[key] = point_count
                counts[key] = veg_count

        print('Point Counts:\n', point_counts)
        return counts

    def calculate_snow_depth(self):
        for key in self.snow_depth_array_dict.keys():
            if self.files[key] != None:
                self.snow_depth_array_dict[key] = []
                print('Calculating snow depth')
                print(key, self.files[key])
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict['New Snow'] or self.grid[i][j].vegetation_flag_dict[key]:
                            pass

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

    def get_max_and_min_intensity(self, scan_basis):
        self.max_intensity = max(self.files[scan_basis].intensity)
        self.min_intensity = min(self.files[scan_basis].intensity)
        return self.max_intensity, self.min_intensity

    def reset_basis_info(self):
        self.stats_key = None
        self.intensity_key = None
        self.max_bound = None
        self.min_bound = None
        self.max_intensity = None
        self.min_intensity = None
        return '-', '-'

    def color_points(self, color_basis, scan_basis, upper_bound, lower_bound):
        vegetation_color = [0, 65535, 0]
        negative_color = [0, 0, 65535]
        positive_color = [65535, 0, 0]

        # SET DEFAULT IF COLOR BASIS NOT SPECIFIED
        if color_basis not in ['intensity', 'depth']:
            color_basis = 'default'
            scan_basis = 'default'

        # SET DEFAULT IF SCAN BASIS NOT SPECIFIED
        if scan_basis not in ['Ground', 'Int. Snow', 'New Snow']:
            color_basis = 'default'
            if self.files['New Snow'] != None:
                scan_basis = 'New Snow'
            elif self.files['Ground'] != None:
                scan_basis = 'Ground'
            elif self.files['Int. Snow'] != None:
                scan_basis = 'Int. Snow'
            else:
                print('No file selected to plot')
                return 'No file selected to plot'

        # ALWAYS RESET COLORING
        for key in [scan_basis, 'New Snow']:
            if self.files[key] != None:
                self.files[key].plot_red = copy.deepcopy(self.files[key].red)
                self.files[key].plot_blue = copy.deepcopy(self.files[key].blue)
                self.files[key].plot_green = copy.deepcopy(self.files[key].green)

        if color_basis == 'default':
            for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if self.grid[i][j].vegetation_flag_dict[scan_basis]:
                            for point in self.grid[i][j].point_arrays[scan_basis]:
                                index = point.index
                                self.files[scan_basis].plot_red[index] = vegetation_color[0]
                                self.files[scan_basis].plot_green[index] = vegetation_color[1]
                                self.files[scan_basis].plot_blue[index] = vegetation_color[2]
            print("Only coloring by vegetation and using default colors.")

        if color_basis == 'intensity':
            print(f'Coloring: intensity scan basis {scan_basis}')
            intensities = self.files[scan_basis].intensity
            intensity_stdev = np.std(np.array(intensities))
            intensity_mean = np.mean(np.array(intensities))
            if upper_bound == '':
                self.upper_bound = intensity_mean+intensity_stdev # self.max_intensity
            else:
                self.upper_bound = float(upper_bound)
            if lower_bound == '':
                self.lower_bound = intensity_mean-intensity_stdev # self.min_intensity
            else:
                self.lower_bound = float(lower_bound)
            
            print('upper bound', upper_bound)
            print('lower bound', lower_bound)
            median = (self.upper_bound + self.lower_bound)/2
            print('median intensity', median)

            for i in range(len(intensities)):
                if intensities[i] < median:
                    # print('Comparison:')
                    # print(intensities[i])
                    # print(len(intensities))
                    # print(len(self.files[scan_basis].plot_red))
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

        if color_basis == 'depth':
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
            
            # for key in ['New Snow']:
            print(f'Coloring: depth scan basis {scan_basis}')
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j].vegetation_flag_dict['New Snow']:
                        for point in self.grid[i][j].point_arrays['New Snow']:
                            index = point.index
                            self.files['New Snow'].plot_red[index] = vegetation_color[0]
                            self.files['New Snow'].plot_green[index] = vegetation_color[1]
                            self.files['New Snow'].plot_blue[index] = vegetation_color[2]

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

        return self.plot_points(color_basis, scan_basis), round(self.upper_bound), round(self.lower_bound)

    def plot_points_initial(self):   
        self.init_canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = self.init_canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(self.files['Ground'].xyz, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        scatter2.set_data(self.files['New Snow'].xyz, edge_color = None, face_color = "blue", size = 4)
        view.add(scatter2)

        view.camera = 'arcball' 
        axis = visuals.XYZAxis(parent=view.scene)
        view.add(axis)

        return self.init_canvas
                
    def plot_points(self, color_basis, scan_basis):
        self.stats_key = scan_basis
        if color_basis in ['default', 'intensity']:
            # print('plot key: ', scan_basis)
            # print(self.files['New Snow'].plot_red)
            # print(self.files['New Snow'].plot_green)
            # print(self.files['New Snow'].plot_blue)
            rgb = np.stack((self.files[scan_basis].plot_red/max(self.files[scan_basis].plot_red), self.files[scan_basis].plot_green/max(self.files[scan_basis].plot_green), self.files[scan_basis].plot_blue/max(self.files[scan_basis].plot_blue)))
            rgb = np.transpose(rgb)
            print(rgb)

            self.scene = Scene(self, self.files[scan_basis].xyz, rgb, color_basis)
            
        if color_basis == 'depth':
            # print('plot key: ', scan_basis)
            print(self.files['New Snow'].plot_red)
            print(self.files['New Snow'].plot_green)
            print(self.files['New Snow'].plot_blue)
            snow_rgb = np.stack((self.files['New Snow'].plot_red/max(self.files['New Snow'].plot_red), self.files['New Snow'].plot_green/max(self.files['New Snow'].plot_green), self.files['New Snow'].plot_blue/max(self.files['New Snow'].plot_blue)))
            snow_rgb = np.transpose(snow_rgb)
            print(snow_rgb)

            self.scene = Scene(self, self.files['New Snow'].xyz, snow_rgb, color_basis)

        return self.scene

    def get_depth_stats(self, points):
        sum_depth = 0
        count = 0
        max_depth = -float('INF')
        min_depth = float('INF')
        # print('points', len(points))
        for point in points:
            print(point)
            i = math.floor((point[0]-self.min_x)/self.cell_size)
            j = math.floor((point[1]-self.min_y)/self.cell_size)
            
            print('Vegetation NS: ', self.grid[i][j].vegetation_flag_dict['New Snow'])
            print(f'Vegetation {self.stats_key}: ', self.grid[i][j].vegetation_flag_dict[self.stats_key])

            if not self.grid[i][j].vegetation_flag_dict['New Snow']:
                # for point in self.grid[i][j].point_arrays['New Snow']:
                depth = self.grid[i][j].depth_dict[self.stats_key]
                print('grid cell:', i, ", ", j, " Depth ", depth)
                if depth > max_depth:
                    max_depth = depth
                if depth < min_depth:
                    min_depth = depth
                sum_depth += depth
                count +=1
            else:
                print("Vegetation cell")
            try:
                average_depth = round(sum_depth/count, 2)
            except:
                average_depth = float('INF')
                    
        return average_depth, round(max_depth, 2), round(min_depth, 2)

    def get_intensity_stats(self, selected):
        intensities = self.files[self.stats_key].intensity[tuple(selected)]
        average = np.mean(intensities)
        max_intensity = max(intensities)
        min_intensity = min(intensities)
        return round(average,2), round(max_intensity, 2), round(min_intensity, 2)



        


    