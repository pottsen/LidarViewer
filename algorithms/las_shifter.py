from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *
import time
import sys
import math

def las_shifter(las_file):
    base_file_input = las_file
    print(base_file_input)
    base_file = File(base_file_input, mode = "r")

    file_name = las_file.split('/')[-1]
    # print("file name1 ", file_name)
    file_name = file_name.split('.')[0]
    # print("file name2 ", file_name)

    shift_file_name = file_name+'_shifted.las'
    shift_file = File(shift_file_name, mode = "w", header = base_file.header)


    x= base_file.x 
    y= base_file.y
    z= base_file.z
    

    angle_x = math.pi/100000
    print("angle x", angle_x*180/math.pi)

    angle_y = math.pi/100000
    print("angle y", angle_y*180/math.pi)

    angle_z = math.pi/100000
    print("angle z", angle_z*180/math.pi)
  
    rotation_x = np.array(([1, 0, 0], [0, math.cos(angle_x), -math.sin(angle_x)], [0, math.sin(angle_x), math.cos(angle_x)]))
    
    rotation_y = np.array(([math.cos(angle_y), 0, math.sin(angle_y)], [0, 1, 0], [-math.sin(angle_y), 0, math.cos(angle_y)]))
    
    rotation_z = np.array(([math.cos(angle_z), -math.sin(angle_z), 0],[math.sin(angle_z), math.cos(angle_z), 0], [0, 0, 1]))

    shift_x = 0.03
    print("shift x", shift_x)
    shift_y = 0.02
    print("shift y", shift_y)
    shift_z = 0.01
    print("shift z", shift_z)

    xyz = np.transpose(np.vstack((x,y,z)))
    # print(rotation_x)
    print('rotating second cloud')
    for i in range(len(xyz)):
        # print("c2[i]", snow_cloud[i])
        coordinates = np.transpose(xyz[i])
        coordinates = np.matmul(rotation_x, coordinates)
        coordinates = np.matmul(rotation_y, coordinates)
        coordinates = np.matmul(rotation_z, coordinates)
        xyz[i] = coordinates

    xyz += [shift_x, shift_y, shift_z]


    shift_file.points = base_file.points
    shift_file.x = xyz[:,0]
    shift_file.y = xyz[:,1]
    shift_file.z = xyz[:,2]
    shift_file.close()

    return shift_file_name

if __name__ == "__main__":
        las_shifter(sys.argv[1])
