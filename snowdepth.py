from laspy.file import File
import numpy as np
from scipy import spatial
from scipy.spatial import *


# baseFile = File('simple.las', mode = "rw")
# shiftFile = File('simple_shifted.las', mode = "rw")

baseFile = File('autzen.las', mode = "rw")
shiftFile = File('autzen_shifted.las', mode = "rw")

#points = infile.points
print(shiftFile.points[0])
points = np.array(baseFile.points)

X = np.array(baseFile.X)
Y = np.array(baseFile.Y)

xyPoints = np.array([X,Y]).T
xyPoints[0] = xyPoints[0] + 2
print(xyPoints[0])
#print("xyPoints \n", xyPoints)

kdTree = spatial.KDTree(xyPoints)
#kdTree = spatial.KDTree(points)
print(range(len(shiftFile.points)))
j=0
for i in range(len(shiftFile.points)):
    #print(i, shiftFile.X[i], shiftFile.Y[i])
    shiftX = np.array(shiftFile.X[i])
    shiftY = np.array(shiftFile.Y[i])
    searchPoint = np.array([shiftX,shiftY]).T
    
    closestPoint = kdTree.query(searchPoint)
    if i == j*10000:
        j = j + 1
        print("Search Point ", searchPoint)
        print("Closest Point ", closestPoint)

"""
# def shift_z(las_file):
#     z = las_file.Z
#     shift = 10
#     return(z+shift)

# shifted_z = shift_z(infile)

# for spec in infile.point_format:
#     print(spec.name)

#specs: [X, Y, Z, intensity, flag_byte, raw_classification, scan_angle_rank, user_data, pt_src_id, gps_time, red, green, blue]

#infile.Z = infile.Z + 1000

#print("10 added to Z values")

#infile.close()

#treeData = np.array[infile.X,infile.Y]
"""

