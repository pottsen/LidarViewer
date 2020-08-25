from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys

def shift_area(las_file):
        base_file_input = las_file
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('/')[-1]
        file_name = file_name.split('.')[0]

        points = base_file.points

        X = base_file.x
        Y = base_file.y
        Z = base_file.z
        max_x = max(X)
        min_x = min(X)
        pct10 = abs(max_x-min_x)/10
        int10 = min_x+pct10
        
        for i in range(len(X)):
            if min_x <= X[i] <= int10:
                # print('here')
                Z[i] += 1

        XYZ = np.stack((X,Y,Z), axis=-1)

        # unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)

        # points = points[unique_indices]

        

        if len(points) > 3000000:
                step = int(np.ceil(len(points)/3000000))
                array = np.arange(0,len(points), step)
                points = points[array]
        
        clean_file_name = file_name+"_10pShift_clean.las"
        clean_file = File(clean_file_name, mode = "w", header = base_file.header)
        clean_file.points = points
        clean_file.x = X
        clean_file.y = Y
        clean_file.z = Z
        clean_file.close()
        return clean_file_name

if __name__ == "__main__":
        shift_area(sys.argv[1])
        