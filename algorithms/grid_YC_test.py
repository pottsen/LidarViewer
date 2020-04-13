from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math
import copy
from remove_duplicates import remove_duplicates
from las_shifter import las_shifter
from iterative_closest_point_clean import *

import vispy.scene
from vispy.scene import visuals


#### TEST

class Point_Class():
    def __init__(self, index, x, y, z, red, green, blue):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.r = red
        self.g = green
        self.b = blue

class Grid_cell():
    def __init__(self):
        self.base_vegetation_flag = False
        self.snow_vegetation_flag = False
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



### make it accept base and snow file at same time?
class Grid():
    def __init__(self, base_file, snow_file, cell_size):
        #do we want to call this here?
        #will probably want to clean up once we get everything written
        self.cell_size = cell_size
        self.max_snow_depth = -float("INF")
        self.min_snow_depth = float("INF")
        self.average_snow_depth = 0
        
        # Load in base file
        self.base_file = File(base_file, mode = "r")
        self.base_file_name = base_file.split('/')[-1]
        self.base_file_name = self.base_file_name.split('.')[0]
        print("base file name ", self.base_file_name)
        self.base_x = self.base_file.x
        print("number of base points", len(self.base_x))
        self.base_y = self.base_file.y
        self.base_z = self.base_file.z 
        self.base_xyz = np.stack((self.base_x, self.base_y, self.base_z))
        self.base_xyz = np.transpose(self.base_xyz)
        self.base_red = copy.deepcopy(self.base_file.red)
        self.base_green = copy.deepcopy(self.base_file.green)
        self.base_blue = copy.deepcopy(self.base_file.blue)
        # self.make_grid_by_cell(self.cell_size)

        # Load in snow file
        self.snow_file = File(snow_file, mode = "r")
        self.snow_file_name = snow_file.split('/')[-1]
        self.snow_file_name = self.snow_file_name.split('.')[0]
        print("snow file name ", self.snow_file_name)
        self.snow_x = -self.snow_file.x
        print("number of snow points", len(self.snow_x))
        self.snow_y = -self.snow_file.y
        self.snow_z = self.snow_file.z 
        self.snow_xyz = np.stack((self.snow_x, self.snow_y, self.snow_z))
        self.snow_xyz = np.transpose(self.snow_xyz)
        self.snow_red = copy.deepcopy(self.snow_file.red)
        self.snow_green = copy.deepcopy(self.snow_file.green)
        self.snow_blue = copy.deepcopy(self.snow_file.blue)


        self.plot_points()
        
        # self.make_grid_by_cell(self.cell_size)
        
        
        # self.make_kd_tree()







    def make_grid_by_cell(self, size_of_cells):
        
        #################################################
        #pull in the base x array and base y array -- max. deltas, and then assigning points to grid cells
        #### USE LOWER CASE x, y, z on self.base_file

        # base_x = self.base_file.x
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

        # base_y = self.base_file.y
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

        # base_z = self.base_file.z
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
        print("\nsnow data")

        # snow_x = -self.snow_file.x
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

        # snow_y = -self.snow_file.y
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

        # snow_z = self.snow_file.z
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

        # base_red = self.base_file.red
        # base_green = self.base_file.green
        # base_blue = self.base_file.blue
        # max_red = max(base_red)
        # max_green = max(base_green)
        # max_blue = max(base_blue)

        
        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        self.max_x = max(self.base_max_x, self.snow_max_x)
        self.min_x = min(self.base_min_x, self.snow_min_x)

        self.max_y = max(self.base_max_y, self.snow_max_y)
        self.min_y = min(self.base_min_y, self.snow_min_y)

        # self.max_x = self.base_max_x
        # self.min_x = self.base_min_x

        # self.max_y = self.base_max_y
        # self.min_y = self.base_min_y

        delta_x = abs(self.max_x - self.min_x)
        delta_y = abs(self.max_y - self.min_y)
        area = float(delta_x)*float(delta_y)

        # print("delta x", round(delta_x, 2))
        # print("delta y", round(delta_y, 2)) 
        # print("area", round(area, 0))

        #################################################
        # number of cells for gridding = delta / size_of_cell
        # cieling used so that we dont cut off the end of the grid/scan
        # print("Size of cells ", self.cell_size, " by ", self.cell_size)

        self.number_of_cells_x = math.ceil(delta_x/self.cell_size)
        # print("# x cells", number_of_cells_x)

        self.number_of_cells_y = math.ceil(delta_y/self.cell_size)
        # print("# y cells", number_of_cells_y)

        print("\nTotal number of grid cells: ", self.number_of_cells_x*self.number_of_cells_y)


        #################################################
        # make grid
        self.grid = [[Grid_cell() for i in range(self.number_of_cells_y)] for j in range(self.number_of_cells_x)]
        print("\nGrid complete")

    def add_points_to_grid(self, flag):
        #################################################
        # add points to grid cells
        if flag == "base":
            # x = self.base_file.x
            # y = self.base_file.y
            # z = self.base_file.z
            # self.base_x = self.base_file.x
            # self.base_y = self.base_file.y
            # self.base_z = self.base_file.z 
            # self.base_xyz = np.stack((self.base_x, self.base_y, self.base_z))
            # self.base_xyz = np.transpose(self.base_xyz)
            # self.base_red = copy.deepcopy(self.base_file.red)
            # self.base_green = copy.deepcopy(self.base_file.green)
            # self.base_blue = copy.deepcopy(self.base_file.blue)
            max_red = max(self.base_red)
            max_green = max(self.base_green)
            max_blue = max(self.base_blue)

            for i in range(len(self.base_file.points)):
                if (i % 1000000) == 0:
                    print(i, " of ", len(self.base_file.points), " base points added to grid")


                grid_x = math.floor((self.base_x[i]-self.min_x)/self.cell_size)
                grid_y = math.floor((self.base_y[i]-self.min_y)/self.cell_size)
                # try:
                point = Point_Class(i, self.base_x[i], self.base_y[i], self.base_z[i], self.base_red[i]/max_red, self.base_green[i]/max_green, self.base_blue[i]/max_blue)
                self.grid[grid_x][grid_y].add_base_point(point)
                # print("point added to grid cell", grid_x, grid_y)
                # except:
                #     print("exception adding point to grid cell", grid_x, grid_y, i)

            print("All base points added to grid cells.")

        elif flag == "snow":
            # x = self.snow_file.x
            # y = self.snow_file.y
            # z = self.snow_file.z 
            # self.snow_x = -self.snow_file.x
            # self.snow_y = -self.snow_file.y
            # self.snow_z = self.snow_file.z 
            # self.snow_xyz = np.stack((self.snow_x, self.snow_y, self.snow_z))
            # self.snow_xyz = np.transpose(self.snow_xyz)
            # self.snow_red = copy.deepcopy(self.snow_file.red)
            # self.snow_green = copy.deepcopy(self.snow_file.green)
            # self.snow_blue = copy.deepcopy(self.snow_file.blue)
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
                    point = Point_Class(i, self.snow_x[i], self.snow_y[i], self.snow_z[i], self.snow_red[i]/max_red, self.snow_green[i]/max_green, self.snow_blue[i]/max_blue)
                    self.grid[grid_x][grid_y].add_snow_point(point)
                    # print("point added to grid cell", grid_x, grid_y)
                    # except:
                    #     print("exception adding point to grid cell", grid_x, grid_y, i)

            print("All snow points added to grid cells.")

    def flag_vegetation(self, flag):
        max_points = 0
        total = 0
        count = 0
        if flag == "base":
            print("Flagging vegetation by base...")
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    # print("# points ", len(self.grid[i][j].base_array))
                    total += len(self.grid[i][j].base_array)
                    # setting this to size_of_cells implies that you have something sticking up at 90deg
                    # which may be too strong for the top of the ridge
                    # self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(2.75*self.cell_size, flag)
                    self.grid[i][j].find_vegetation(4*self.cell_size, flag)
                    if self.grid[i][j].base_vegetation_flag == True:
                        count += 1
                        # print("i ", i, " j ", j, )
                        # print(count, " of ", number_of_cells_y*number_of_cells_x)
                    
                    if len(self.grid[i][j].base_array) > max_points:
                        max_points = len(self.grid[i][j].base_array)
                        # max_i = i
                        # max_j = j

        if flag == "snow":
            print("Flagging vegetation by snow...")
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    # print("# points ", len(self.grid[i][j].snow_array))
                    total += len(self.grid[i][j].snow_array)
                    # setting this to size_of_cells implies that you have something sticking up at 90deg
                    # which may be too strong for the top of the ridge
                    # self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(2.75*self.cell_size, flag)
                    self.grid[i][j].find_vegetation(4*self.cell_size, flag)
                    if self.grid[i][j].snow_vegetation_flag == True:
                        count += 1
                        # print("i ", i, " j ", j, )
                        # print(count, " of ", number_of_cells_y*number_of_cells_x)
                    
                    if len(self.grid[i][j].snow_array) > max_points:
                        max_points = len(self.grid[i][j].snow_array)
                        # max_i = i
                        # max_j = j

        print('\nmax number of points ', max_points)
        print("Total points in grid cells", total)
        print(count, " cells with vegetation out of ", self.number_of_cells_y*self.number_of_cells_x)
    """
    def add_snow_points(self, snow_file):
        self.snow_las_file = snow_file
    
        self.snow_file = File(self.snow_las_file, mode = "rw")

        self.snow_file_name = snow_file.split('/')[-1]
        self.snow_file_name = snow_file.split('.')[0]
        print("Snow file name ", self.snow_file_name)
        
        snow_x = self.snow_file.x
        snow_y = self.snow_file.y
        snow_z = self.snow_file.z

        snow_red = self.snow_file.red
        snow_green = self.snow_file.green
        snow_blue = self.snow_file.blue
        max_red = max(snow_red)
        max_green = max(snow_green)
        max_blue = max(snow_blue)

        #add points to coresponding grid cells
        for i in range(len(self.snow_file.points)):
            if snow_x[i] > self.max_x or snow_x[i] < self.min_x or snow_y[i] > self.max_y or snow_y[i] < self.min_y:
                print("Snow point out of grid range")
            else:
                if (i % 1000000) == 0:
                    print(i, " of ", len(self.base_file.points), " snow points added to grid")

                grid_x = math.floor((snow_x[i]-self.min_x)/self.cell_size)
                grid_y = math.floor((snow_y[i]-self.min_y)/self.cell_size)
                try:
                    point = Point_Class(i, snow_x[i], snow_y[i], snow_z[i], snow_red[i]/max_red, snow_green[i]/max_green, snow_blue[i]/max_blue)
                    self.grid[grid_x][grid_y].add_snow_point(point)
                    # print("point added to grid cell", grid_x, grid_y)
                except:
                    print("exception adding snow point to grid cell", grid_x, grid_y, i)

        print("All snow points added to grid cells.")
    """  

    def calculate_snow_depth(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].vegetation_flag:
                    pass
                    # print("vegetation encountered")
                
                else:
                    self.grid[i][j].calculate_average_base_z()
                    self.grid[i][j].calculate_average_snow_z()
                    if (len(self.grid[i][j].snow_array) > 0 and len(self.grid[i][j].base_array) > 0):
                        self.grid[i][j].depth = self.grid[i][j].snow_average_z -  self.grid[i][j].base_average_z
                        # print(self.grid[i][j].depth)
                    
                    
                        self.average_snow_depth += self.grid[i][j].depth
                        
                        ## store max and min depths for coloring
                        if self.grid[i][j].depth > self.max_snow_depth:
                            self.max_snow_depth = self.grid[i][j].depth

                        if self.grid[i][j].depth < self.min_snow_depth:
                            self.min_snow_depth = self.grid[i][j].depth
                    else:
                        # print("no snow or base points")
                        pass

        self.average_snow_depth = self.average_snow_depth/(len(self.grid)*len(self.grid[0]))

        print("Max Depth: ", self.max_snow_depth)
        print("Min Depth: ", self.min_snow_depth)
        print("Average Depth: ", self.average_snow_depth)
    

    def color_points(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].snow_vegetation_flag or self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].snow_array)):

                        self.snow_red[self.grid[i][j].snow_array[k].index] = 0
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 0
                
                elif self.grid[i][j].base_vegetation_flag or self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 0
                        self.base_blue[self.grid[i][j].base_array[k].index] = 0
                
                ### ADD COLORING BY SNOW DEPTH?
                """
                else:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])

                        self.snow_green[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                        self.snow_blue[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                """

    def plot_points(self):   

        # base_xyz = np.stack((self.base_file.x, self.base_file.y, self.base_file.z))
        # base_xyz = np.transpose(base_xyz)
        # print(base_xyz)
        # snow_xyz = np.stack((self.snow_file.x, self.snow_file.y, self.snow_file.z))
        # snow_xyz = np.transpose(snow_xyz)
        base_rgb = np.stack((self.base_red/max(self.base_red), self.base_green/max(self.base_green), self.base_blue/max(self.base_blue)))
        # print(base_rgb)
        base_rgb = np.transpose(base_rgb)
        # print(base_rgb)
        snow_rgb = np.stack((self.snow_red/max(self.snow_red), self.snow_green/max(self.snow_green), self.snow_blue/max(self.snow_blue)))
        snow_rgb = np.transpose(snow_rgb)
        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 3)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        # scatter2.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 3)
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = snow_rgb, size = 4)
        view.add(scatter2)

        # scatter3 = visuals.Markers()
        # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = "blue", size = 2)
        # # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = snow_rgb, size = 2)
        # view.add(scatter3)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()

    def align_point_clouds(self):
        # PASS FULL CLOUDS, BUT ONLY MATCH ON CLIFFS
        base_cliff_indices = []
        snow_cliff_indices = []
        ### store indices of points from grid cells
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].base_vegetation_flag:
                    for k in range(len(self.grid[i][j].base_array)):
                        base_cliff_indices.append(self.grid[i][j].base_array[k].index)
                if self.grid[i][j].snow_vegetation_flag:
                    for l in range(len(self.grid[i][j].snow_array)):
                        snow_cliff_indices.append(self.grid[i][j].snow_array[l].index)

        print("Index arrays made")
        # print("Base\n", base_indices)
        # print("Snow\n", snow_indices)

        # base_cliff_points = self.base_file.points[base_cliff_indices]
        # snow_cliff_points = self.snow_file.points[snow_cliff_indices]
        # snow_match_points = self.snow_file.points[snow_cliff_indices]

        base_cliff_x = self.base_x[base_cliff_indices]
        base_cliff_y = self.base_y[base_cliff_indices]
        base_cliff_z = self.base_z[base_cliff_indices]
        
        snow_cliff_x = self.snow_x[snow_cliff_indices]
        snow_cliff_y = self.snow_y[snow_cliff_indices]
        snow_cliff_z = self.snow_z[snow_cliff_indices]

        # match_x = snow_match_points.x
        # match_y = snow_match_points.y
        # match_z = snow_match_points.z

        base_cliff_xyz = np.stack((base_cliff_x, base_cliff_y, base_cliff_z))
        base_cliff_xyz = np.transpose(base_cliff_xyz)

        snow_cliff_xyz = np.stack((snow_cliff_x, snow_cliff_y, snow_cliff_z))
        snow_cliff_xyz = np.transpose(snow_cliff_xyz)

        snow_original_cliff_xyz = copy.deepcopy(snow_cliff_xyz)
        # match_xyz = np.transpose(base_xyz)

        snow_cliff_match, iteration, error = icp_algorithm(base_cliff_xyz, snow_cliff_xyz)

        rotation, translation = calculate_rotation_translation(snow_cliff_match, snow_original_cliff_xyz, snow_cliff_match)

        print("rotation", rotation, "\ntranslation", translation)

        # for i in range(len(snow_original_xyz)):
        #     snow_original_xyz[i] = np.matmul(rotation, snow_original_xyz[i]) + translation

        self.snow_matched_xyz = []
        self.snow_matched_xyz = copy.deepcopy(self.snow_xyz)
        # print(self.matched_snow_xyz)

        for i in range(len(self.snow_matched_xyz)):
            self.snow_matched_xyz[i] = np.matmul(rotation, self.snow_matched_xyz[i]) + translation

        error = calculate_error(self.snow_matched_xyz[snow_cliff_indices], snow_cliff_match)

        print("\nError", error)


        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(base_cliff_xyz, edge_color = None, face_color = "red", size = 3)
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 5)
        view.add(scatter)
        scatter2 = visuals.Markers()
        scatter2.set_data(snow_cliff_match, edge_color = None, face_color = "blue", size = 3)
        # scatter2.set_data(self.snow_matched_xyz, edge_color = None, face_color = "blue", size = 5)
        view.add(scatter2)
        scatter3 = visuals.Markers()
        scatter3.set_data(snow_original_cliff_xyz, edge_color = None, face_color = "green", size = 3)
        # scatter3.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 5)
        view.add(scatter3)
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        # Axes are x=red, y=green, z=blue
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()



    def regrid_point_cloud(self):
        # ONCE ALIGNED REGRID THE CLOUD THAT WAS SHIFTED
        print("Regridding Point Cloud..")
        self.snow_array = []
        self.snow_total_z = 0
        max_red = max(self.snow_red)
        max_green = max(self.snow_green)
        max_blue = max(self.snow_blue)
        for i in range(len(self.snow_xyz)):
            if self.snow_matched_xyz[i][0] > self.max_x or self.snow_matched_xyz[i][0] < self.min_x or self.snow_matched_xyz[i][1] > self.max_y or self.snow_matched_xyz[i][1] < self.min_y:
                print("Snow point out of grid range")
            else:
                if (i % 1000000) == 0:
                    print(i, " of ", len(self.base_file.points), " snow points added to grid")
                grid_x = math.floor((self.snow_matched_xyz[i][0]-self.min_x)/self.cell_size)
                grid_y = math.floor((self.snow_matched_xyz[i][1]-self.min_y)/self.cell_size)
                # try:
                point = Point_Class(i, self.snow_matched_xyz[i][0], self.snow_matched_xyz[i][1], self.snow_matched_xyz[i][2], self.snow_red[i]/max_red, self.snow_green[i]/max_green, self.snow_blue[i]/max_blue)
                self.grid[grid_x][grid_y].add_snow_point(point)
                # print("point added to grid cell", grid_x, grid_y)
                # except:
                #     print("exception adding point to grid cell", grid_x, grid_y, i)

        print("All snow points added to grid cells.")

    def flag_cliffs(self):
        # FLAG CLIFFS, NOT JUST VEGETATION
        # Use reflectivities to find cliffs

        pass

    def export_cliffs(self):
        base_cliff_indices = []
        snow_cliff_indices = []
        ### store indices of points from grid cells
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].vegetation_flag:
                    for k in range(len(self.grid[i][j].base_array)):
                        base_cliff_indices.append(self.grid[i][j].base_array[k].index)
                    for l in range(len(self.grid[i][j].snow_array)):
                        snow_cliff_indices.append(self.grid[i][j].snow_array[l].index)

        print("Index arrays made")
        # print("Base\n", base_indices)
        # print("Snow\n", snow_indices)

        base_cliff_points = self.base_file.points[base_cliff_indices]
        snow_cliff_points = self.snow_file.points[snow_cliff_indices]

        base_cliff_file_name = self.base_file_name + "_cliffs.las"
        snow_cliff_file_name = self.snow_file_name + "_cliffs.las"

        base_cliff_file = File(base_cliff_file_name, mode = "w", header = self.base_file.header)
        snow_cliff_file = File(snow_cliff_file_name, mode = "w", header = self.snow_file.header)

        base_cliff_file.points = base_cliff_points
        snow_cliff_file.points = snow_cliff_points

        base_cliff_file.close()
        snow_cliff_file.close()

    def initialize_alignment(self):
        print("Running initial alignment...")
        rotation_matrix, translation = initial_alignment(self.base_xyz, self.snow_xyz)

        for i in range(len(self.snow_xyz)):
            self.snow_xyz[i] = np.matmul(rotation_matrix, self.snow_xyz[i]) + translation

        self.base_x = self.base_xyz[:,0]
        self.base_y = self.base_xyz[:,1]
        self.base_z = self.base_xyz[:,2]

        self.snow_x = self.snow_xyz[:,0]
        self.snow_y = self.snow_xyz[:,1]
        self.snow_z = self.snow_xyz[:,2]

        

     
###################################################
# # Ubuntu
# grid = Grid("../../las_data/points_clean.las", 500)
start = time.time()
# clean_base_file = remove_duplicates("../../las_data/nz_base.las")
# clean_base_file = remove_duplicates("../../las_data/On_Snow_LiftShack.las")
clean_base_file = remove_duplicates("../../las_data/OnSnow_cliffs.las")

# clean_snow_file = remove_duplicates("../../las_data/nz_snow.las")
# clean_snow_file = remove_duplicates("../../las_data/LiftBalcony_LiftShack.las")
clean_snow_file = remove_duplicates("../../las_data/LiftBalcony_cliffs.las")

grid = Grid(clean_base_file, clean_snow_file, 1)


###################################################
# # Windows
# grid = Grid("../../../Documents/YC_LiftDeck_10Dec19.las", 100)
## start = time.time()

#test ICP here


# clean_file = remove_duplicates("C:/Users/peter/OneDrive/Documents/LiftDeck2.las")
## clean_file = remove_duplicates("C:/Users/peter/Downloads/pointclouds_nz/Scan_3.las")
## grid = Grid(clean_file, 1)
# snow_file = las_shifter(clean_file)
# grid.add_snow_points(snow_file)

# grid.add_snow_points("C:/Users/peter/OneDrive/Documents/LiftDeck2_shifted.las")
## grid.add_snow_points("C:/Users/peter/Downloads/pointclouds_nz/Scan_8.las")




#######################################################
# # Run Algorithms
# grid.initialize_alignment()
# grid.plot_points()

grid.make_grid_by_cell(0.25)

grid.add_points_to_grid("base")
grid.add_points_to_grid("snow")

print("Flagging vegetation...")
grid.flag_vegetation("base")
grid.flag_vegetation("snow")

print("Aligning point clouds...")
grid.align_point_clouds()

# grid.regrid_point_cloud()

# print("store indices")
# grid.export_cliffs()

# print("\nCalculating snow depth...")
# grid.calculate_snow_depth()


"""
print("store indices")
grid.export_cliffs()
"""

# print("Coloring points")
# grid.color_points()
end = time.time()
print("\nComputation Time: " + str((end - start)/60) + " minutes")

# print("Plotting...")
# grid.plot_points()


    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
        


