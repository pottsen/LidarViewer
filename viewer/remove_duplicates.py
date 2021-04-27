from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys

# function goes through and removes duplicate points from a las file
def remove_duplicates(las_file):
        base_file_input = las_file
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('/')[-1]
        file_name = file_name.split('.')[0]

        points = base_file.points

        X = base_file.x
        Y = base_file.y
        Z = base_file.z

        XYZ = np.stack((X,Y,Z), axis=-1)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)

        points = points[unique_indices]

        
        # down samples points if greater than 3 million
        if len(points) > 3000000:
                step = int(np.ceil(len(points)/3000000))
                array = np.arange(0,len(points), step)
                points = points[array]
        
        # saves clean file
        clean_file_name = file_name+"_clean.las"
        clean_file = File(clean_file_name, mode = "w", header = base_file.header)
        clean_file.points = points
        clean_file.close()
        return clean_file_name