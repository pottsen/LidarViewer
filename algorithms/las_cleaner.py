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

def classify_points(las_file):
        classify_file_input = las_file
        print("Input file: ", classify_file_input)
        classify_file = File(classify_file_input, mode = "rw")

        X = classify_file.X
        print("Number of Points: ", len(X))
        Y = classify_file.Y
        # print("Y ", len(Y))


        XY = np.stack((X,Y), axis = -1)
        unique_XY, unique_XY_indices = np.unique(XY, return_index=True, axis=0)
        # print(unique_XY)
        print("unique_XY", len(unique_XY))
        print("unique_XY_indices",len(unique_XY_indices))

        classify_file.raw_classification[:] = 0
        
        """
        points with classification 1 will be used in the calculations but
        further work may need to be done to speicfy use in depth calculations
        to not get bad calcs
        """
        
        classify_file.raw_classification[unique_XY_indices] = 1
        # print(XY)
        # print(classify_file.raw_classification[:])
        classify_file.close()




if __name__ == "__main__":
        clean_file_name = remove_duplicates(sys.argv[1])
        # classify_points(clean_file_name)
