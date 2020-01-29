from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys

def remove_duplicates(las_file):
        base_file_input = las_file
        print(base_file_input)
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('.')[0]
        print("file name", file_name)

        points = base_file.points

        X = base_file.X
        print("X ", len(X))

        Y = base_file.Y
        print("Y ", len(Y))

        Z = base_file.Z
        print("Z ", len(Z))

        XYZ = np.stack((X,Y,Z), axis=-1)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)
        print(unique_XYZ)
        print(XYZ)
        print("unique_XYZ", len(unique_XYZ))
        print("unique_indices",len(unique_indices))

        points = points[unique_indices]
        
        clean_file_name = file_name+"_clean.las"
        clean_file = File(clean_file_name, mode = "w", header = base_file.header)
        clean_file.points = points
        clean_file.close()
        return clean_file_name