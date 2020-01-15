from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math

class Point_Class():
    def __init__(self, index, x, y, z):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        # print(self.index, self.x, self.y, self.z)

class Grid_cell():
    def __init__(self):
        self.mid_x = None
        self.mid_y = None
        self.point_array = []
    
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

    # add points to kdTree
    def add_point(self, point):
        self.point_array.append(point)

    def calculate_average(self):
        pass


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
        self.grid = self.make_grid_by_cell(self.cell_size)
        # self.make_kd_tree()
        
    def make_grid_by_cell(self, size_of_cells):
        #################################################
        #pull in the base x array and base y array -- max. deltas, and then assigning points to grid cells
        base_x = self.base_file.X
        max_x = np.max(base_x)
        print("max x ", max_x)
        min_x = np.min(base_x)
        print("min x ", min_x)

        base_y = self.base_file.Y
        max_y = np.max(base_y)
        print("max y ", max_y)
        min_y = np.min(base_y)
        print("min y ", min_y)

        base_z = self.base_file.Z

        ################################################
        # calculate x and y length of scan to be used in determing grid spots
        delta_x = abs(max_x - min_x)
        delta_y = abs(max_y - min_y)

        print("delta x", delta_x)
        print("delta y", delta_y)

        area = float(delta_x)*float(delta_y)
        print("area", area)

        #################################################
        # number of cells for gridding = delta / size_of_cell
        # cieling used so that we dont cut off the end of the grid/scan
        print("Size of cells ", size_of_cells, " by ", size_of_cells)
        number_of_cells_x = math.ceil(delta_x/size_of_cells)
        print("# x cells", number_of_cells_x)
        number_of_cells_y = math.ceil(delta_y/size_of_cells)
        print("# y cells", number_of_cells_y)


        #################################################
        # make grid
        self.grid = [[Grid_cell() for i in range(number_of_cells_y)] for j in range(number_of_cells_x)]
        print("Grid complete")

        #################################################
        # add points to grid cells
        for i in range(len(self.base_file.points)):
            if (i % 1000000) == 0:
                print(i, " of ", len(self.base_file.points), " points added to grid")


            grid_x = math.floor((base_x[i]-min_x)/size_of_cells)
            grid_y = math.floor((base_y[i]-min_y)/size_of_cells)
            try:
                point = Point_Class(i, base_x[i], base_y[i], base_z[i])
                self.grid[grid_x][grid_y].add_point(point)
                # print("point added to grid cell", grid_x, grid_y)
            except:
                print("exception adding point to grid cell", grid_x, grid_y, i)

        print("All points added to grid cells.")

        max_points = 0
        total = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # print("# points ", len(self.grid[i][j].point_array))
                total += len(self.grid[i][j].point_array)
                if len(self.grid[i][j].point_array) > max_points:
                    max_points = len(self.grid[i][j].point_array)

        print('max number of points ', max_points)
        print("Total points in grid cells", total)
        # x_pointer = min_x + grid_x_size/2
        # print("x pointer", x_pointer)
        # y_pointer = min_y + grid_y_size/2
        # print("y pointer", y_pointer)
        # mid_x = x_pointer
        # self.grid_cells = []
        # for i in range(int(number_of_cells)):
        #     mid_y = y_pointer
        #     for j in range(int(number_of_cells)):
        #         self.grid_cells.append(Grid_cell(mid_x, mid_y))
        #         # print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_x)
        #         # print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_y)
        #         mid_y += grid_y_size
        #     mid_x += grid_x_size

        
        # self.grid_cells = np.asarray(self.grid_cells)

        # mid_x_vec = np.vectorize(Grid_cell.get_mid_x, otypes=[object])
        # mid_y_vec = np.vectorize(Grid_cell.get_mid_y, otypes=[object])
        
        # mid_x_array = mid_x_vec(self.grid_cells)
        # mid_y_array = mid_y_vec(self.grid_cells)

        # mid_x_array = np.vstack(mid_x_array)
        # mid_y_array = np.vstack(mid_y_array)
        # self.mid_xy_array = [mid_x_array, mid_y_array]
        

        # print(self.mid_xy_array)


    def make_kd_tree(self):
        self.grid_cell_tree = spatial.cKDTree(self.mid_x_array)


        

grid = Grid("../../las_data/points_clean.las", 500)



    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
        


