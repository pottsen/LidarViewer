from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math
from remove_duplicates import remove_duplicates

import vispy.scene
from vispy.scene import visuals

class Point_Class():
    def __init__(self, index, x, y, z):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        # print(self.index, self.x, self.y, self.z)

class Grid_cell():
    def __init__(self):
        self.vegetation_flag = False
        self.mid_x = None
        self.mid_y = None
        self.point_array = []
        self.snow_array = []
        self.max_z = -float("INF")
        self.min_z = float("INF")
        self.delta_z = 0
        self.base_total_z = 0
        self.snow_total_z = 0
        self.depth = 0

    
    # def __init__(self, mid_x, mid_y):
    #     self.mid_x = mid_x
    #     self.mid_y = mid_y
    #     self.point_array = []
    
    def set_mid_x(self, mid_x):
        self.mid_x = mid_x

    def set_mid_y(self, mid_y):
        self.mid_y = mid_y
    
    def get_mid_x(self):
        return self.mid_x

    def get_mid_y(self):
        return self.mid_y

    def add_point(self, point):
        self.point_array.append(point)
        self.base_total_z +=point.z
        #########################################
        # ADD THIS IN?
        # if point.z > self.max_z:
        #     self.max_z = point.z
        # if point.z < self.min_z:
        #     self.min_z = point.z

        # self.delta_z = abs(self.max_z - self.min_z)
        # self.find_vegetation(100)
    
    def add_snow_point(self, point):
        self.snow_array.append(point)
        self.snow_total_z += point.z

    def calculate_average_base_z(self):
        if len(self.point_array) > 0:
            self.base_average_z = self.base_total_z/len(self.point_array)
        else:
            # print("No base points in grid cell")
            pass

    def calculate_average_snow_z(self):
        if len(self.snow_array) > 0:
            self.snow_average_z = self.snow_total_z/len(self.snow_array)
        else:
            # print("No snow points in grid cell")
            pass

    def find_vegetation(self, height):
        ##########################################
        # find max and min z of the cell
        # should I put this in the add_point function?
        self.min_z = float("INF")
        self.max_z = -float("INF")
        for point in self.point_array:
            if point.z < self.min_z:
                self.min_z = point.z
            if point.z > self.max_z:
                self.max_z = point.z
        if abs(self.max_z - self.min_z) > height and abs(self.max_z - self.min_z) != float("INF"):
            # print("delta z ", abs(self.max_z - self.min_z))
            # print("vegetation found")
            self.vegetation_flag = True




class Grid():
    def __init__(self, las_file, cell_size):
        #do we want to call this here?
        #will probably want to clean up once we get everything written
        self.las_file = las_file
        self.cell_size = cell_size
        
        print(self.las_file)
        self.base_file = File(self.las_file, mode = "rw")

        self.file_name = las_file.split('.')[0]
        print(self.file_name)
        self.make_grid_by_cell(self.cell_size)
        # self.make_kd_tree()
        
    def make_grid_by_cell(self, size_of_cells):
        
        # # Find out what the point format looks like.
        # print("point format")
        # pointformat = self.base_file.point_format
        # for spec in pointformat:
        #     print(spec.name)

        # print(max(self.base_file.blue/65535))
        # # #Like XML or etree objects instead?
        # # a_mess_of_xml = pointformat.xml()
        # # an_etree_object = pointformat.etree()

        # # #It looks like we have color data in this file, so we can grab:
        # # blue = inFile.blue
        # print("\nheader format")
        # #Lets take a look at the header also.
        # headerformat = self.base_file.header.header_format
        # for spec in headerformat:
        #     print(spec.name)

        # print(self.base_file.header.max)
        # print(self.base_file.header.min)
        
        #################################################
        #pull in the base x array and base y array -- max. deltas, and then assigning points to grid cells
        #### USE LOWER CASE x, y, z on self.base_file
        base_x = self.base_file.x
        self.max_x = np.max(base_x)
        self.min_x = np.min(base_x)

        if round(self.max_x,2) != round(self.base_file.header.max[0], 2):
            print("x max coordinate mismatch")
            print("max x of points ", round(self.max_x,2))
            print("max x ", round(self.base_file.header.max[0], 2))
    
        if round(self.min_x,2) != round(self.base_file.header.min[0], 2):
            print("x min coordinate mismatch")
            print("min x of points ", round(self.min_x,2))
            print("min x ", round(self.base_file.header.min[0], 2))

        base_y = self.base_file.y
        self.max_y = np.max(base_y)
        self.min_y = np.min(base_y)

        if round(self.max_y,2) != round(self.base_file.header.max[1], 2):
            print("y max coordinate mismatch")
            print("max y of points ", round(self.max_y,2))
            print("max y ", round(self.base_file.header.max[1], 2))
        
        if round(self.min_y,2) != round(self.base_file.header.min[1], 2):
            print("y min coordinate mismatch")
            print("min y of points ", round(self.min_y,2))
            print("min y ", round(self.base_file.header.min[1], 2))

        base_z = self.base_file.z
        self.max_z = np.max(base_z)
        self.min_z = np.min(base_z)

        if round(self.max_z,2) != round(self.base_file.header.max[2], 2):
            print("z max coordinate mismatch")
            print("max z of points ", round(self.max_z,2))
            print("max z ", round(self.base_file.header.max[2], 2))

        if round(self.min_z,2) != round(self.base_file.header.min[2], 2):
            print("z min coordinate mismatch")
            print("min z of points ", round(self.min_z,2))
            print("min z ", round(self.base_file.header.min[2], 2))

        
        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(self.max_x - self.min_x)
        delta_y = abs(self.max_y - self.min_y)
        area = float(delta_x)*float(delta_y)

        print("delta x", round(delta_x, 2))
        print("delta y", round(delta_y, 2)) 
        print("area", round(area, 0))

        #################################################
        # number of cells for gridding = delta / size_of_cell
        # cieling used so that we dont cut off the end of the grid/scan
        print("Size of cells ", size_of_cells, " by ", size_of_cells)

        number_of_cells_x = math.ceil(delta_x/size_of_cells)
        # print("# x cells", number_of_cells_x)

        number_of_cells_y = math.ceil(delta_y/size_of_cells)
        # print("# y cells", number_of_cells_y)

        print("Total number of grid cells: ", number_of_cells_x*number_of_cells_y)


        #################################################
        # make grid
        self.grid = [[Grid_cell() for i in range(number_of_cells_y)] for j in range(number_of_cells_x)]
        print("Grid complete")

        #################################################
        # add points to grid cells
        for i in range(len(self.base_file.points)):
            if (i % 1000000) == 0:
                print(i, " of ", len(self.base_file.points), " points added to grid")


            grid_x = math.floor((base_x[i]-self.min_x)/self.cell_size)
            grid_y = math.floor((base_y[i]-self.min_y)/self.cell_size)
            try:
                point = Point_Class(i, base_x[i], base_y[i], base_z[i])
                self.grid[grid_x][grid_y].add_point(point)
                # print("point added to grid cell", grid_x, grid_y)
            except:
                print("exception adding point to grid cell", grid_x, grid_y, i)

        print("All points added to grid cells.")

        max_points = 0
        total = 0
        count = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # print("# points ", len(self.grid[i][j].point_array))
                total += len(self.grid[i][j].point_array)
                self.grid[i][j].find_vegetation(10)
                if self.grid[i][j].vegetation_flag == True:
                    count += 1
                    # print("i ", i, " j ", j, )
                    # print(count, " of ", number_of_cells_y*number_of_cells_x)
                
                if len(self.grid[i][j].point_array) > max_points:
                    max_points = len(self.grid[i][j].point_array)
                    # max_i = i
                    # max_j = j

        print('max number of points ', max_points)
        print("Total points in grid cells", total)
        print(count, " cells with vegetation out of ", number_of_cells_y*number_of_cells_x)

    def add_snow_points(self, snow_file):
        self.snow_las_file = snow_file
    
        self.snow_file = File(self.snow_las_file, mode = "rw")

        self.snow_file_name = snow_file.split('.')[0]
        print(self.snow_file_name)
        
        snow_x = self.snow_file.x
        snow_y = self.snow_file.y
        snow_z = self.snow_file.z

        #add points to coresponding grid cells
        for i in range(len(self.base_file.points)):
            if snow_x[i] > self.max_x or snow_x[i] < self.min_x or snow_y[i] > self.max_y or snow_y[i] < self.min_y:
                print("Snow point out of grid range")
            else:
                if (i % 1000000) == 0:
                    print(i, " of ", len(self.base_file.points), " snow points added to grid")

                grid_x = math.floor((snow_x[i]-self.min_x)/self.cell_size)
                grid_y = math.floor((snow_y[i]-self.min_y)/self.cell_size)
                try:
                    point = Point_Class(i, snow_x[i], snow_y[i], snow_z[i])
                    self.grid[grid_x][grid_y].add_snow_point(point)
                    # print("point added to grid cell", grid_x, grid_y)
                except:
                    print("exception adding snow point to grid cell", grid_x, grid_y, i)

        print("All snow points added to grid cells.")
        
    def calculate_snow_depth(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].vegetation_flag:
                    pass
                    # print("vegetation encountered")
                
                else:
                    self.grid[i][j].calculate_average_base_z()
                    self.grid[i][j].calculate_average_snow_z()
                    if (len(self.grid[i][j].snow_array) > 0 and len(self.grid[i][j].point_array) > 0):
                        self.grid[i][j].depth = self.grid[i][j].snow_average_z -  self.grid[i][j].base_average_z
                        # print(self.grid[i][j].depth)
                    else:
                        # print("no snow or base points")
                        pass
                    
                    ## POINT BY POINT COMPARISON
                    # for snow_point in self.grid[i][j].snow_array:
                    #     closest_distance = float("INF")
                    #     for base_point in self.grid[i][j].point_array:
                    #         distance = (snow_point.x - base_point.x)**2 + (snow_point.y - base_point.y)**2
                    #         if distance < closest_distance:
                    #             closest_distance = distance
                    #             depth = snow_point.z - base_point.z
                    #     print("distance", closest_distance, "depth", depth)

    def plot_points(self):
        base_xyz = np.stack((self.base_file.x, self.base_file.y, self.base_file.z))
        base_xyz = np.transpose(base_xyz)
        # print(base_xyz)
        snow_xyz = np.stack((self.snow_file.x, self.snow_file.y, self.snow_file.z))
        snow_xyz = np.transpose(snow_xyz)
        base_rgb = np.stack((self.base_file.red/max(self.base_file.red), self.base_file.green/max(self.base_file.green), self.base_file.blue/max(self.base_file.blue)))
        # print(base_rgb)
        base_rgb = np.transpose(base_rgb)
        # print(base_rgb)
        snow_rgb = np.stack((self.snow_file.red/max(self.snow_file.red), self.snow_file.green/max(self.snow_file.green), self.snow_file.blue/max(self.snow_file.blue)))
        snow_rgb = np.transpose(snow_rgb)
        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        scatter.set_data(base_xyz, edge_color = None, face_color = base_rgb, size = 3)
        scatter2 = visuals.Markers()
        scatter2.set_data(snow_xyz, edge_color = None, face_color = snow_rgb, size = 5)
        view.add(scatter)
        # view.add(scatter2)
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()

     
###################################################
# # Ubuntu
# grid = Grid("../../las_data/points_clean.las", 500)

###################################################
# # Windows
# grid = Grid("../../../Documents/YC_LiftDeck_10Dec19.las", 100)
start = time.time()

clean_file = remove_duplicates("C:/Users/peter/OneDrive/Documents/LiftDeck2.las")
grid = Grid(clean_file, 1)
grid.add_snow_points("C:/Users/peter/OneDrive/Documents/LiftDeck2_shifted.las")
print("Calculating snow depth...")
grid.calculate_snow_depth()

end = time.time()
print("Computation Time: " + str((end - start)/60) + " minutes")

print("Plotting...")
grid.plot_points()

    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
        


