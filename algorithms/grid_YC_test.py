from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys
import math
import copy
from remove_duplicates import remove_duplicates
from las_shifter import las_shifter
from iterative_closest_point_clean import *
import matplotlib.pyplot as plt


import vispy.scene
from vispy.scene import visuals


#### TEST
 
class Point_Class():
    def __init__(self, index, x, y, z, red, green, blue, intensity):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.r = red
        self.g = green
        self.b = blue
        self.intensity = intensity

class Grid_cell():
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
        
        # ##### Down sample if needed
        # if len(self.base_xyz) > 5000000:
        #     base_xyz_indices = signal.resample(self.base_xyz, 5000000)

        # print("downsample", base_xyz_indices)

        try:
            self.base_red = copy.deepcopy(self.base_file.red)
            self.base_green = copy.deepcopy(self.base_file.green)
            self.base_blue = copy.deepcopy(self.base_file.blue)
        except:
            self.base_red = np.ones(len(self.base_file.points)) * 65535
            self.base_green = np.ones(len(self.base_file.points)) * 65535
            self.base_blue = np.ones(len(self.base_file.points)) * 65535

        print("red", self.base_red)

        self.base_intensity = copy.deepcopy(self.base_file.intensity)
        # self.make_grid_by_cell(self.cell_size)

        # Load in snow file
        self.snow_file = File(snow_file, mode = "r")
        self.snow_file_name = snow_file.split('/')[-1]
        self.snow_file_name = self.snow_file_name.split('.')[0]
        print("snow file name ", self.snow_file_name)
        # self.snow_x = -self.snow_file.x
        self.snow_x = self.snow_file.x
        print("number of snow points", len(self.snow_x))
        # self.snow_y = -self.snow_file.y
        self.snow_y = self.snow_file.y
        self.snow_z = self.snow_file.z 
        self.snow_xyz = np.stack((self.snow_x, self.snow_y, self.snow_z))
        self.snow_xyz = np.transpose(self.snow_xyz)
        print("test")
        print(self.snow_xyz[0])
        print(self.snow_file.points[0])
        # mesh = np.meshgrid(self.snow_xyz)
        # print("mesh grid", mesh[0])

        ##### Down sample if needed
        # if len(self.snow_xyz) > 5000000:
        #     self.snow_xyz = signal.resample(t=self.snow_xyz, 5000000)

        try:
            self.snow_red = copy.deepcopy(self.snow_file.red)
            self.snow_green = copy.deepcopy(self.snow_file.green)
            self.snow_blue = copy.deepcopy(self.snow_file.blue)
        except:
            self.snow_red = np.ones(len(self.snow_file.points)) * 65535
            self.snow_green = np.ones(len(self.snow_file.points)) * 65535
            self.snow_blue = np.ones(len(self.snow_file.points)) * 65535

        self.snow_intensity = copy.deepcopy(self.snow_file.intensity)


        # # Find out what the point format looks like.
        # print("point format")
        # pointformat = self.base_file.point_format
        # for spec in pointformat:
        #     print(spec.name)

        # self.plot_points_initial()

        _ = plt.hist(self.base_file.Intensity, bins='auto', cumulative = True) #, range = (-0.5, 0.5))# np.histogram(snow_depth_array)
        plt.title("Histogram with 'auto' bins")
        plt.show()
        self.plot_points_intensity()
        
        # self.make_grid_by_cell(self.cell_size)
        
        
        # self.make_kd_tree()


    def plot_points_intensity(self):
        base_red = copy.deepcopy(self.base_red)
        base_green = copy.deepcopy(self.base_green)
        base_blue = copy.deepcopy(self.base_blue)
        intensity = copy.deepcopy(self.base_intensity)

        max_intensity = max(intensity)
        
        for i in range(len(intensity)):
            # YC 12/5 and 12/10
            intensity_threshold = 420000

            # initial
            # intensity_threshold = 42000

            if intensity[i] < intensity_threshold:
                base_red[i] = 65535
                base_blue[i] = 0.0
                base_green[i] = 0.0

            else:
                base_red[i] = intensity[i]/max_intensity*65535
                base_blue[i] = intensity[i]/max_intensity*65535
                base_green[i] = 65535

        base_rgb = np.stack((base_red/65535, base_green/65535, base_blue/65535))
        base_rgb = np.transpose(base_rgb)
        print(base_rgb)



        # print(base_rgb)
        # base_rgb = np.transpose(base_rgb)
        # print(base_rgb)
        # snow_rgb = np.stack((self.snow_red/max(self.snow_red), self.snow_green/max(self.snow_green), self.snow_blue/max(self.snow_blue)))
        # snow_rgb = np.transpose(snow_rgb)
        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 2)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 3)
        # scatter2.set_data(self.snow_xyz, edge_color = None, face_color = snow_rgb, size = 4)
        view.add(scatter2)

        # scatter3 = visuals.Markers()
        # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = "blue", size = 2)
        # # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = snow_rgb, size = 2)
        # view.add(scatter3)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()        




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
                point = Point_Class(i, self.base_x[i], self.base_y[i], self.base_z[i], self.base_red[i]/max_red, self.base_green[i]/max_green, self.base_blue[i]/max_blue, self.base_intensity[i])
                self.grid[grid_x][grid_y].add_base_point(point)

                if self.base_intensity[i] < 40000:
                        self.grid[grid_x][grid_y].base_intensity_flag = True
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
                    point = Point_Class(i, self.snow_x[i], self.snow_y[i], self.snow_z[i], self.snow_red[i]/max_red, self.snow_green[i]/max_green, self.snow_blue[i]/max_blue, self.snow_intensity[i])
                    self.grid[grid_x][grid_y].add_snow_point(point)
                    if self.snow_intensity[i] < 40000:
                        self.grid[grid_x][grid_y].snow_intensity_flag = True
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
                    # if self.grid[i][j].base_intensity_flag == False:
                    self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(2.75*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(6*self.cell_size, flag)
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
                    # if self.grid[i][j].snow_intensity_flag == False:
                    self.grid[i][j].find_vegetation(math.tan(math.pi/3)*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(2.75*self.cell_size, flag)
                    # self.grid[i][j].find_vegetation(6*self.cell_size, flag)
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

        print("Max Depth: ", self.max_snow_depth)
        print("Min Depth: ", self.min_snow_depth)
        print("Average Depth: ", self.average_snow_depth)

        _ = plt.hist(snow_depth_array, bins='auto')#, range = (-0.5, 0.5))# np.histogram(snow_depth_array)
        plt.title("Histogram with 'auto' bins")
        plt.show()

    

    def color_points(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].snow_vegetation_flag or self.grid[i][j].base_vegetation_flag:
                # if self.grid[i][j].snow_vegetation_flag or self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].snow_array)):

                        self.snow_red[self.grid[i][j].snow_array[k].index] = 0
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 0

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 0
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 65535
                        self.base_blue[self.grid[i][j].base_array[k].index] = 0

                elif self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].snow_array)):
                        # self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_red[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])

                        self.snow_green[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )

                        # self.snow_blue[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].base_array)):
                        # self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        self.base_red[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].base_array[k].index, self.base_file.red[self.grid[i][j].base_array[k].index])

                        self.base_green[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )

                        # self.base_blue[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.base_blue[self.grid[i][j].base_array[k].index] = 65535
                
                elif self.grid[i][j].depth == 0:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 32770
                        # self.snow_red[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])

                        self.snow_green[self.grid[i][j].snow_array[k].index] = 32770

                        # self.snow_blue[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 32770

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 32770
                        # self.base_red[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].base_array[k].index, self.base_file.red[self.grid[i][j].base_array[k].index])

                        self.base_green[self.grid[i][j].base_array[k].index] = 32770

                        # self.base_blue[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.base_blue[self.grid[i][j].base_array[k].index] = 32770
                
                else:
                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        # self.snow_red[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])

                        self.snow_green[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                        self.snow_blue[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        # self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        # self.base_red[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.min_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].base_array[k].index, self.base_file.red[self.grid[i][j].base_array[k].index])

                        self.base_green[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                        self.base_blue[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        # self.base_blue[self.grid[i][j].base_array[k].index] = 65535
                
                """
                # elif self.grid[i][j].depth < (-1):
                elif (self.grid[i][j].snow_intensity_flag and self.grid[i][j].snow_vegetation_flag) or (self.grid[i][j].base_intensity_flag and self.grid[i][j].base_vegetation_flag):
                # elif self.grid[i][j].base_vegetation_flag or self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 0
                        self.base_blue[self.grid[i][j].base_array[k].index] = 0

                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 0
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 0

                # elif self.grid[i][j].depth < 0.025 and self.grid[i][j].depth > 0:
                # elif self.grid[i][j].depth < 0.05 and self.grid[i][j].depth > 0:
                elif self.grid[i][j].depth < 0.1 and self.grid[i][j].depth > 0:
                # elif self.grid[i][j].base_vegetation_flag or self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 0
                        self.base_blue[self.grid[i][j].base_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 0
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535
                
                elif self.grid[i][j].depth < 0:
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 0
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 65535
                        self.base_blue[self.grid[i][j].base_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 0
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535

                elif self.grid[i][j].depth < -2:
                    for k in range(len(self.grid[i][j].base_array)):
                        self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.base_green[self.grid[i][j].base_array[k].index] = 0
                        self.base_blue[self.grid[i][j].base_array[k].index] = 0

                    for k in range(len(self.grid[i][j].snow_array)):
                        self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])
                        self.snow_green[self.grid[i][j].snow_array[k].index] = 0
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 0
                ### ADD COLORING BY SNOW DEPTH?
                
                else:
                    for k in range(len(self.grid[i][j].snow_array)):
                        # self.snow_red[self.grid[i][j].snow_array[k].index] = 65535
                        self.snow_red[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].snow_array[k].index, self.base_file.red[self.grid[i][j].snow_array[k].index])

                        self.snow_green[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                        # self.snow_blue[self.grid[i][j].snow_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.snow_blue[self.grid[i][j].snow_array[k].index] = 65535

                    for k in range(len(self.grid[i][j].base_array)):
                        # self.base_red[self.grid[i][j].base_array[k].index] = 65535
                        self.base_red[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        # print("index ", self.grid[i][j].base_array[k].index, self.base_file.red[self.grid[i][j].base_array[k].index])

                        self.base_green[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )

                        # self.base_blue[self.grid[i][j].base_array[k].index] = int( (self.grid[i][j].depth)/(self.max_snow_depth)*65535 )
                        self.base_blue[self.grid[i][j].base_array[k].index] = 65535
                """

    def plot_points_initial(self):   

        # base_rgb = np.stack((self.base_red/max(self.base_red), self.base_green/max(self.base_green), self.base_blue/max(self.base_blue)))
        # print(base_rgb)
        # base_rgb = np.transpose(base_rgb)
        # print(base_rgb)
        # snow_rgb = np.stack((self.snow_red/max(self.snow_red), self.snow_green/max(self.snow_green), self.snow_blue/max(self.snow_blue)))
        # snow_rgb = np.transpose(snow_rgb)
        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 4)
        # scatter2.set_data(self.snow_xyz, edge_color = None, face_color = snow_rgb, size = 4)
        view.add(scatter2)

        # scatter3 = visuals.Markers()
        # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = "blue", size = 2)
        # # scatter3.set_data(self.snow_matched_xyz, edge_color = None, face_color = snow_rgb, size = 2)
        # view.add(scatter3)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()
    
    def plot_points(self):   

        # base_xyz = np.stack((self.base_file.x, self.base_file.y, self.base_file.z))
        # base_xyz = np.transpose(base_xyz)
        # print(base_xyz)
        # snow_xyz = np.stack((self.snow_file.x, self.snow_file.y, self.snow_file.z))
        # snow_xyz = np.transpose(snow_xyz)
        base_rgb = np.stack((self.base_red/max(self.base_red), self.base_green/max(self.base_green), self.base_blue/max(self.base_blue)))
        # print(base_rgb)
        base_rgb = np.transpose(base_rgb)
        # print("base_rgb", base_rgb)
        snow_rgb = np.stack((self.snow_red/max(self.snow_red), self.snow_green/max(self.snow_green), self.snow_blue/max(self.snow_blue)))
        snow_rgb = np.transpose(snow_rgb)
        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 2)
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 3)
        view.add(scatter)
        
        scatter2 = visuals.Markers()
        # scatter2.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 3)
        scatter2.set_data(self.snow_xyz, edge_color = None, face_color = snow_rgb, size = 2)
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
                # if self.grid[i][j].snow_vegetation_flag and self.grid[i][j].snow_intensity_flag == False and self.grid[i][j].base_array != [] and  self.grid[i][j].snow_array != []:
                if self.grid[i][j].snow_vegetation_flag and self.grid[i][j].base_array != [] and  self.grid[i][j].snow_array != []:
                    for k in range(len(self.grid[i][j].base_array)):
                        base_cliff_indices.append(self.grid[i][j].base_array[k].index)
                    for l in range(len(self.grid[i][j].snow_array)):
                        snow_cliff_indices.append(self.grid[i][j].snow_array[l].index)
                # if self.grid[i][j].snow_vegetation_flag:
                # if self.grid[i][j].snow_vegetation_flag and self.grid[i][j].snow_intensity_flag == False:
                #     for l in range(len(self.grid[i][j].snow_array)):
                #         snow_cliff_indices.append(self.grid[i][j].snow_array[l].index)
                        

        print("Index arrays made")
        print("Base points size\n", len(base_cliff_indices))
        print("Snow points size\n", len(snow_cliff_indices))

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
        scatter.set_data(base_cliff_xyz, edge_color = None, face_color = "red", size = 4)
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)
        scatter2 = visuals.Markers()
        scatter2.set_data(snow_cliff_match, edge_color = None, face_color = "blue", size = 4)
        # scatter2.set_data(self.snow_matched_xyz, edge_color = None, face_color = "blue", size = 4)
        view.add(scatter2)
        scatter3 = visuals.Markers()
        scatter3.set_data(snow_original_cliff_xyz, edge_color = None, face_color = "green", size = 4)
        # scatter3.set_data(self.snow_xyz, edge_color = None, face_color = "green", size = 4)
        view.add(scatter3)
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        # Axes are x=red, y=green, z=blue
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()

        # matched_file_name = self.snow_file_name +'_matched.las'
        # matched_file = File(matched_file_name, mode = "w", header = self.snow_file.header)
        # matched_file.points = self.snow_file.points
        # matched_file.x = self.snow_matched_xyz[:,0]
        # matched_file.y = self.snow_matched_xyz[:,1]
        # matched_file.z = self.snow_matched_xyz[:,2]
        # matched_file.close()



    def regrid_point_cloud(self):
        # ONCE ALIGNED REGRID THE CLOUD THAT WAS SHIFTED
        print("Regridding Point Cloud..")
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.snow_array = []
                self.snow_max_z = -float("INF")
                self.snow_min_z = float("INF")
                self.snow_delta_z = 0
                self.snow_total_z = 0
                self.depth = 0

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
                point = Point_Class(i, self.snow_matched_xyz[i][0], self.snow_matched_xyz[i][1], self.snow_matched_xyz[i][2], self.snow_red[i]/max_red, self.snow_green[i]/max_green, self.snow_blue[i]/max_blue, self.snow_intensity[i])
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

    def tie_point_error(self):
        print("Calculating Tie Point Error:")
        print("Making trees..")
        base_tree = spatial.cKDTree(self.base_xyz)
        snow_tree = spatial.cKDTree(self.snow_xyz)

        ######## BC Scan 1
        # LookersRight
        # snow_tie_points = [[-12.979106, -261.574128, 1732.78212], [-12.648628, -319.262555, 1745.626416], [-13.517328, -108.493827, 1687.991239]]
        # snow_tp_indices = [36901, 39998, 33591]
        # LookersLeft
        # base_tie_points = [[-12.791863, -261.608945, 1732.800418], [-12.772755, -319.273812, 1745.343716], [-13.558948, -108.43461, 1687.963776]]
        # base_tp_indices = [36349, 36733, 31823]

        ######## Lift Shack
        # Lift Balcony
        # base_tie_points = [[-427.650349, -837.341975, 2927.88136], [-555.438164, -828.128651, 2987.397632]]
        # base_tp_indices = [814572, 461567]
        # On Snow
        # snow_tie_points = [[-427.58228, -837.413667, 2927.735315], [-555.539838, -828.076453, 2987.205581]]
        # snow_tp_indices = [265581, 156224] 
        
        ######### Test5 and Test10
        # Test10
        # base_tie_points = [[-704.858655, -250.928919, 2815.650352], [-894.031537, -136.883815, 2858.912302]]
        # Test 10 for test5 big
        base_tie_points = [[-704.858655, -250.928919, 2815.650352], [-900.301597, 73.905413, 2845.349185]]
        # base_tp_indices = [4024008,  268708]

        # Test5
        # snow_tie_points = [[-704.858655, -250.928919, 2815.650352], [-893.585119, -137.797877, 2859.365728]]
        # Test5 big
        snow_tie_points = [[-704.858655, -250.928919, 2815.650352], [-900.306196 , 73.957415, 2845.182149]]
        # snow_tp_indices = [948812,  20731]
        """
        Original error
        Total:  1.1167521875000246
        Normalized:  0.5583760937500123
        Match error
        Total:  0.9651570217744727
        Normalized:  0.48257851088723636
        """


        ######### Cliffs
        """
        ## Original Error:
        ## Total:  0.09865093749995223
        ## Normalized:  0.03288364583331741
        ## Match error
        ## Total:  0.037359259362686054
        ## Normalized:  0.012453086454228685
        """
        ## Lift Balcony
        # base_tie_points = [[-710.589053, -232.794525, 2814.560238], [-836.109332, -265.927537, 2892.579737], [-898.181519, -112.218379, 2857.614506]]
        # base_tp_indices = [1024539,  278226,   23014]
        ## On Snow
        # snow_tie_points = [[-710.600795, -232.817664, 2814.398774], [-836.101498, -265.969774, 2892.424745], [-898.058942, -112.37893, 2857.511832]]
        # snow_tp_indices = [1104461,  318444,   18474]
        
        
        print("Querying the trees...")
        base_tp_indices = base_tree.query(base_tie_points)[1]
        snow_tp_indices = snow_tree.query(snow_tie_points)[1]

        print("Base Indices: ", base_tp_indices)
        print("Snow Indices: ", snow_tp_indices)

        base_tie_points = self.base_xyz[base_tp_indices]
        snow_tie_points = self.snow_xyz[snow_tp_indices]
        match_tie_points = self.snow_matched_xyz[snow_tp_indices]

        tie_point_original_error = 0.0
        tie_point_matched_error = 0.0

        for i in range(len(base_tp_indices)):
            original_error = 0.0
            matched_error = 0.0
            for j in range(len(self.base_xyz[base_tp_indices[i]])):
                original_error += (float(self.base_xyz[base_tp_indices[i],j]) - float(self.snow_xyz[snow_tp_indices[i],j]))**2
                matched_error += (float(self.base_xyz[base_tp_indices[i],j]) - float(self.snow_matched_xyz[snow_tp_indices[i],j]))**2
            tie_point_original_error += original_error
            tie_point_matched_error += matched_error
            print("Point ", i, "\nOriginal Point Error: ", original_error, "\nOriginal Normalized Error: ", tie_point_original_error/(i+1))
            print("Point ", i, "\nMatched Point Error: ", matched_error, "\nMatched Normalized Error: ", tie_point_matched_error/(i+1))

        normalized_tp_orig_error = tie_point_original_error/len(base_tie_points)
        normalized_tp_match_error = tie_point_matched_error/len(base_tie_points)

        # print("Original error\n Total: ", tie_point_original_error, "\n Normalized: ", normalized_tp_orig_error)
        # print("Match error\n Total: ", tie_point_matched_error, "\n Normalized: ", normalized_tp_match_error)

        # tie_point_original_error = 0.0
        # tie_point_matched_error = 0.0

        # for i in range(len(base_tie_points)):
        #     for j in range(len(base_tie_points[0])):
        #         # print("base:", float(base_tie_points[i,j]))
        #         # print("snow:", float(snow_tie_points[i,j]))
        #         # print("match:", float(match_tie_points[i,j]))
        #         tie_point_original_error += (float(base_tie_points[i,j]) - float(snow_tie_points[i,j]))**2
        #         tie_point_matched_error += (float(base_tie_points[i,j]) - float(match_tie_points[i,j]))**2
        
        normalized_tp_orig_error = tie_point_original_error/len(base_tie_points)
        normalized_tp_match_error = tie_point_matched_error/len(base_tie_points)

        print("Original error\n Total: ", tie_point_original_error, "\n Normalized: ", normalized_tp_orig_error)
        print("Match error\n Total: ", tie_point_matched_error, "\n Normalized: ", normalized_tp_match_error)

    def save_match_file(self):
        print("Saving matched snow file...")
        points = self.snow_matched_xyz
        
        match_file_name = self.snow_file_name+"_match.las"
        match_file = File(match_file_name, mode = "w", header = self.snow_file.header)
        match_file.points = self.snow_file.points
        match_file.x = self.snow_matched_xyz[:,0]
        match_file.y = self.snow_matched_xyz[:,1]
        match_file.z = self.snow_matched_xyz[:,2]
        match_file.close()

start = time.time()

###################################################
# # Ubuntu
# grid = Grid("../../las_data/points_clean.las", 500)

# clean_base_file = remove_duplicates("../../las_data/nz_base.las")
# clean_base_file = remove_duplicates("../../las_data/On_Snow_LiftShack.las")
# clean_base_file = remove_duplicates("../../las_data/OnSnow_cliffs.las")

# clean_snow_file = remove_duplicates("../../las_data/nz_snow.las")
# clean_snow_file = remove_duplicates("../../las_data/LiftBalcony_LiftShack.las")
# clean_snow_file = remove_duplicates("../../las_data/LiftBalcony_cliffs.las")

###################################################
# # Windows
# grid = Grid("../../../Documents/YC_LiftDeck_10Dec19.las", 100)

# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_cliffs2.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_cliffs2.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_cliffs_smallTP.las")
# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftDeck_test10.las")

# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersRight_BC_May15.las")
clean_base_file = remove_duplicates("../viewer/LiftDeck_1210_cliffs_right_of_fin_prebomb_smaller.las")

# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_LiftShack2.las")

# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersRight_BC.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersRight_3TP.las")

# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_shack.las")


# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_cliffs2.las") #LiftBalcony looks like bigger scan, extent-wise
# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_cliffs2.las") #LiftBalcony looks like bigger scan, extent-wise
# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_cliffs_smallTP.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_test5.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_test5_big2.las")

# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersLeft_BC_May15.las")
clean_snow_file = remove_duplicates("../viewer/LiftDeck_1210_cliffs_right_of_fin_postbomb.las")

# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_LiftShack2.las")

# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersLeft_BC2.las")
# clean_base_file = remove_duplicates("C:/Users/peter/Research/las_data/LookersLeft_3TP.las")

# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/OnSnow_cliffs2.las")
# clean_snow_file = remove_duplicates("C:/Users/peter/Research/las_data/LiftBalcony_shack.las")

# clean_snow_file = las_shifter(clean_base_file)


# clean_file = remove_duplicates("C:/Users/peter/OneDrive/Documents/LiftDeck2.las")
## clean_file = remove_duplicates("C:/Users/peter/Downloads/pointclouds_nz/Scan_3.las")
## grid = Grid(clean_file, 1)
# snow_file = las_shifter(clean_file)
# grid.add_snow_points(snow_file)

# grid.add_snow_points("C:/Users/peter/OneDrive/Documents/LiftDeck2_shifted.las")
## grid.add_snow_points("C:/Users/peter/Downloads/pointclouds_nz/Scan_8.las")




#######################################################
# grid = Grid(clean_base_file, clean_snow_file, 0.5)
grid = Grid(clean_base_file, clean_snow_file, 1)


# # Run Algorithms
# grid.initialize_alignment()
# grid.plot_points()


grid.make_grid_by_cell(0.25)

grid.add_points_to_grid("base")
grid.add_points_to_grid("snow")

print("Flagging vegetation...")
grid.flag_vegetation("base")
grid.flag_vegetation("snow")

# print("Aligning point clouds...")
grid.align_point_clouds()
# grid.save_match_file()

# print("Regridding point clouds...")
# grid.regrid_point_cloud()

# print("store indices")
# grid.export_cliffs()

print("\nCalculating snow depth...")
grid.calculate_snow_depth()



# print("store indices")
# grid.export_cliffs()


print("Coloring points")
grid.color_points()
end = time.time()
print("\nComputation Time: " + str((end - start)/60) + " minutes")

grid.tie_point_error()

print("Plotting...")
grid.plot_points()




    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
    



