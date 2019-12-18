from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys

class Point_Class():
    def __init__(self, point):
        self.point = point

class Grid_cell():
    def __init__(self, mid_x, mid_y):
        self.mid_x = mid_x
        self.mid_y = mid_y
        self.point_array = []
    
    def get_mid_x(self):
        return self.mid_x

    def get_mid_y(self):
        return self.mid_y

    def add_point(self, point):
        self.point_array.append(point)

    def calculate_average(self):
        pass


class Grid():
    def __init__(self, las_file, grid_size, number_of_cells):
        self.las_file = las_file
        self.grid_size = grid_size
        self.number_of_cells = number_of_cells
        
        print(self.las_file)
        self.base_file = File(self.las_file, mode = "rw")

        self.file_name = las_file.split('.')[0]
        print(self.file_name)
        self.grid = self.make_grid_by_cell(self.number_of_cells)
        self.make_kd_tree()
        

    def make_grid_by_cell(self, number_of_cells):
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

        #calculate full x and y length of scan
        delta_x = abs(max_x - min_x)
        delta_y = abs(max_y - min_y)

        print("abs x", delta_x)
        print("abs y", delta_y)

        area = float(delta_x)*float(delta_y)
        print("area", area)

        #calculate grid cell size
        grid_x_size = float(delta_x/(number_of_cells))
        grid_y_size = float(delta_y/(number_of_cells))

        x_pointer = min_x + grid_x_size/2
        print("x pointer", x_pointer)
        y_pointer = min_y + grid_y_size/2
        print("y pointer", y_pointer)
        mid_x = x_pointer
        self.grid_cells = []
        for i in range(int(number_of_cells)):
            mid_y = y_pointer
            for j in range(int(number_of_cells)):
                self.grid_cells.append(Grid_cell(mid_x, mid_y))
                print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_x)
                print("grid cell ", len(self.grid_cells), " ", self.grid_cells[-1].mid_y)
                mid_y += grid_y_size
            mid_x += grid_x_size

        
        self.grid_cells = np.asarray(self.grid_cells)

        mid_x_vec = np.vectorize(Grid_cell.get_mid_x, otypes=[object])
        mid_y_vec = np.vectorize(Grid_cell.get_mid_y, otypes=[object])
        
        mid_x_array = mid_x_vec(self.grid_cells)
        mid_y_array = mid_y_vec(self.grid_cells)

        mid_x_array = np.vstack(mid_x_array)
        mid_y_array = np.vstack(mid_y_array)
        self.mid_xy_array = [mid_x_array, mid_y_array]
        

        print(self.mid_xy_array)

    def make_kd_tree(self):
        self.grid_cell_tree = spatial.cKDTree(self.mid_x_array)


        

grid = Grid("../../las_data/points_clean.las", 0, 2)



    # def make_grid(grid_size):
    #     pass

    # if __name__ == "__main__":
    #     grid = Grid(sys.argv[1], 0, 4)
        


