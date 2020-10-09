from laspy.file import File
import numpy as np
from scipy import spatial, signal
from scipy.spatial import *
import time
import sys
import vispy.scene
from vispy.scene import visuals

def print_stats(las_file):
        base_file_input = las_file
        base_file = File(base_file_input, mode = "r")

        file_name = las_file.split('/')[-1]
        file_name = file_name.split('.')[0]

        points = base_file.points

        print(base_file.header)

        X = base_file.x
        Y = base_file.y
        Z = base_file.z

        print()

        print(max(X), min(X))
        print(max(X)- min(X))
        print(max(Y), min(Y))
        print(max(Y)- min(Y))
        print(max(Z), min(Z))
        print(max(Z)- min(Z))


        XYZ = np.stack((X,Y,Z), axis=-1)

        unique_XYZ, unique_indices = np.unique(XYZ, return_index=True, axis=0)

        points = points[unique_indices]


        canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        view = canvas.central_widget.add_view()
        scatter = visuals.Markers()
        # scatter.set_data(self.base_xyz, edge_color = None, face_color = base_rgb, size = 4)
        scatter.set_data(XYZ, edge_color = None, face_color = "red", size = 4)
        view.add(scatter)
        
        view.camera = 'arcball' #'turntable'  # or try 'arcball'
        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=view.scene)
        vispy.app.run()

if __name__ == "__main__":
        print_stats(sys.argv[1])