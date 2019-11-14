from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys

def remove_duplicates(las_file):
        base_file_input = las_file
        print(base_file_input)
        base_file = File(base_file_input, mode = "rw")

        file_name = las_file.split('.')[0]
        print(file_name)

        points = base_file.points

        X = base_file.X
        print("X ", len(X))

        Y = base_file.Y
        print("Y ", len(Y))

        Z = base_file.Z
        print("Z ", len(Z))

        XYZ = np.stack((X,Y,Z), axis=-1)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)
        # print("unique_XYZ", len(unique_XYZ))
        # print("unique_indices",len(unique_indices))


        unique_points = np.take(points, unique_indices, axis = 0)
        # print("size unique",len(unique_points))
        non_unique_points = np.delete(points, unique_indices, axis=0)
        # print("size non unique",len(non_unique_points))
        # print("size total",(len(unique_points)+ len(non_unique_points)))

        base_file.raw_classification[:] = 0
        
        """
        points with classification 1 will be used in the calculations but
        further work may need to be done to speicfy use in depth calculations
        to not get bad calcs
        """
        base_file.raw_classification[unique_indices] = 1
        # print(XY)
        # print(classify_file.raw_classification[:])
        base_file.close()




def classify_points(las_file):
        classify_file_input = las_file
        print("Input file: ", classify_file_input)
        classify_file = File(classify_file_input, mode = "rw")

        points = classify_file.points

        X = classify_file.X
        print("Number of Points: ", len(X))
        Y = classify_file.Y
        # print("Y ", len(Y))


        XY = np.stack((X,Y), axis = -1)
        unique_XY, unique_XY_indices = np.unique(XY, return_index=True, axis=0)
        # print(unique_XY)
        # print("unique_XY", len(unique_XY))
        print("unique_XY_indices",len(unique_XY_indices))

        unique_XY_points = np.take(points, unique_XY_indices, axis = 0)
        print("size unique",len(unique_XY_points))
        non_unique_XY_points = np.delete(points, unique_XY_indices, axis=0)
        print("size non unique",len(non_unique_XY_points))
        # print("size total",(len(unique_points)+ len(non_unique_points)))

        file_name = las_file.split('.')[0]
        redundant_file_name = file_name+"_reduntant.las"
        redundant_file = File(redundant_file_name, mode = "w", header = classify_file.header)
        redundant_file.points = non_unique_XY_points

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

        
        redundant_file.close()

# def clean_trees(las_file):
#         tree_file_input = las_file
#         print("Input file: ", tree_file_input)
#         tree_file = File(tree_file_input, mode = "rw")

#         X = tree_file.X
#         print("Number of Points: ", len(X))
#         Y = tree_file.Y
#         # print("Y ", len(Y))


if __name__ == "__main__":
        clean_file_name = remove_duplicates(sys.argv[1])
        # classify_points(clean_file_name)

"""
def remove_duplicates(las_file):
        base_file_input = las_file
        print(base_file_input)
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('.')[0]
        print(file_name)

        points = base_file.points

        X = base_file.X
        print("X ", len(X))

        Y = base_file.Y
        print("Y ", len(Y))

        Z = base_file.Z
        print("Z ", len(Z))

        XYZ = np.stack((X,Y,Z), axis=-1)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)
        # print("unique_XYZ", len(unique_XYZ))
        # print("unique_indices",len(unique_indices))


        unique_points = np.take(points, unique_indices, axis = 0)
        # print("size unique",len(unique_points))
        non_unique_points = np.delete(points, unique_indices, axis=0)
        # print("size non unique",len(non_unique_points))
        # print("size total",(len(unique_points)+ len(non_unique_points)))
        
        clean_file_name = file_name+"_clean.las"
        clean_file = File(clean_file_name, mode = "w", header = base_file.header)
        clean_file.points = unique_points
        clean_file.close()
        return clean_file_name

def classify_points(las_file):
        classify_file_input = las_file
        print("Input file: ", classify_file_input)
        classify_file = File(classify_file_input, mode = "rw")

        points = classify_file.points

        X = classify_file.X
        print("Number of Points: ", len(X))
        Y = classify_file.Y
        # print("Y ", len(Y))


        XY = np.stack((X,Y), axis = -1)
        unique_XY, unique_XY_indices = np.unique(XY, return_index=True, axis=0)
        # print(unique_XY)
        # print("unique_XY", len(unique_XY))
        print("unique_XY_indices",len(unique_XY_indices))

        unique_XY_points = np.take(points, unique_XY_indices, axis = 0)
        print("size unique",len(unique_XY_points))
        non_unique_XY_points = np.delete(points, unique_XY_indices, axis=0)
        print("size non unique",len(non_unique_XY_points))
        # print("size total",(len(unique_points)+ len(non_unique_points)))

        file_name = las_file.split('.')[0]
        redundant_file_name = file_name+"_reduntant.las"
        redundant_file = File(redundant_file_name, mode = "w", header = classify_file.header)
        redundant_file.points = non_unique_XY_points

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

        
        redundant_file.close()

# def clean_trees(las_file):
#         tree_file_input = las_file
#         print("Input file: ", tree_file_input)
#         tree_file = File(tree_file_input, mode = "rw")

#         X = tree_file.X
#         print("Number of Points: ", len(X))
#         Y = tree_file.Y
#         # print("Y ", len(Y))


if __name__ == "__main__":
        clean_file_name = remove_duplicates(sys.argv[1])
        classify_points(clean_file_name)
"""