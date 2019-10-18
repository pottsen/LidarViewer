from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys

def las_cleaner(las_file):
        base_file_input = las_file
        print(base_file_input)
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('.')[0]
        print(file_name)

        points = np.array(base_file.points)

        X = np.array(base_file.X)
        print("X ", len(X))
        Y = np.array(base_file.Y)
        print("Y ", len(Y))
        Z = np.array(base_file.Z)
        print("Z ", len(Z))

        XYZ = np.stack((X,Y,Z), axis=-1)
        # XYZ = np.sort(XYZ, axis = 0)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)
        print(unique_XYZ)
        # unique_by_Y, indicesY = np.unique(XY, return_index=True, axis=1) 
        print("unique_XYZ", len(unique_XYZ))
        print("unique_indices",len(unique_indices))

        # points = np.sort(points, 0)
        points = points[unique_indices]
        print("points", len(points))


        clean_file = File(file_name+"_clean.las", mode = "w", header = base_file.header)
        clean_file.points = points
        clean_file.close()

if __name__ == "__main__":
        las_cleaner(sys.argv[1])