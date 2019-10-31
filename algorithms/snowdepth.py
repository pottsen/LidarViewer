from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys


def depth_calculator(las_files):
        base_file_input = las_files[1]
        # print(base_file_input)
        snow_file_input = las_files[2]
        # print(snow_file_input)

        base_file = File(base_file_input, mode = "r")
        snow_file = File(snow_file_input, mode = "r")

        # points = np.array(base_file.points)

        base_classification = snow_file.raw_classification
        print(base_classification)
        base_indices = np.where(base_classification ==1)
        
        base_X = base_file.X[base_indices]
        # print("base_X ", len(base_X))

        base_Y = base_file.Y[base_indices]
        # print("base_Y ", len(base_Y))

        base_Z = base_file.Z[base_indices]
        # print("base_Z ", len(base_Z))

        snow_classification = snow_file.raw_classification
        print(snow_classification)
        snow_indices = np.where(snow_classification ==1)
        
        snow_X = snow_file.X[base_indices]
        # print("snow_X ", len(snow_X))

        snow_Y = snow_file.Y[base_indices]
        # print("snow_Y ", len(snow_Y))

        snow_Z = snow_file.Z[base_indices]
        # print("snow_Z ", len(snow_Z))

        base_XY = np.stack((base_X,base_Y), axis=-1)
        snow_XY = np.stack((snow_X,snow_Y), axis=-1)
        print("Created XY arrays")

        np.random.shuffle(base_XY)

        print("Building Tree of size ", len(base_XY))
        start = time.time()
        kdTree = spatial.cKDTree(base_XY)
        end = time.time()
        print("KDTree Loading: " + str(end - start) + " seconds")

        np.random.shuffle(snow_XY)

        print("Querying Tree with data of size ", len(snow_XY))
        start = time.time()
        indices = kdTree.query(snow_XY)[1]
        end = time.time()
        print("KDTree Query: " + str(end - start) + " seconds")

        depths = snow_Z - base_Z[indices]

        print("Mean depth: " + str(np.mean(depths)))
        print("Max depth: " + str(np.max(depths)))
        print("Min depth: " + str(np.min(depths)))

if __name__ == "__main__":
        depth_calculator(sys.argv)


