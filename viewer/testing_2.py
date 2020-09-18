from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys
import vispy.scene
from vispy.scene import visuals

def print_stats(las_file, las_file2):
        base_file_input = las_file
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('/')[-1]
        file_name = file_name.split('.')[0]

        points = base_file.points

        X = base_file.x
        Y = base_file.y
        Z = base_file.z

        print(max(X), min(X))
        print(max(X)- min(X))
        print(max(Y), min(Y))
        print(max(Y)- min(Y))
        print(max(Z), min(Z))
        print(max(Z)- min(Z))


        XYZ = np.stack((X,Y,Z), axis=-1)

        base_file_input2 = las_file2
        base_file2 = File(base_file_input2, mode = "r")

        points2 = base_file2.points
        X2 = base_file2.x
        Y2 = base_file2.y
        Z2 = base_file2.z
        XYZ2 = np.stack((X2,Y2,Z2), axis=-1)


        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)

        points = points[unique_indices]


        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        scatter.set_data(XYZ, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)

        scatter2 = visuals.Markers()
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        scatter2.set_data(XYZ2, edge_color = None, face_color = "green", size = 4)
        view.add(scatter2)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()

if __name__ == "__main__":
        print_stats(sys.argv[1], sys.argv[2])