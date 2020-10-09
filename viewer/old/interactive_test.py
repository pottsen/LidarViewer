import numpy as np
import sys
from vispy import app, visuals, scene
from laspy.file import File

class Canvas(scene.SceneCanvas):
    """ A simple test canvas for testing the EditLineVisual """

    def __init__(self):
        scene.SceneCanvas.__init__(self, keys='interactive',
                                   size=(800, 800), show=True)

        # # Create some initial points
        self.unfreeze()
        # Add a ViewBox to let the user zoom/rotate
        self.view = self.central_widget.add_view()
        self.view.camera = 'arcball' #'turntable'
        # self.view.camera.fov = 30
        self.show()
        self.selected_point = None
        scene.visuals.XYZAxis(parent=self.view.scene)
        self.freeze()

    def on_mouse_press(self, event):
        #1=left, 2=right , 3=middle button
        if event.button == 1:
            p2 = event.pos
            norm = np.mean(self.view.camera._viewbox.size)

            if self.view.camera._event_value is None or len(self.view.camera._event_value) == 2:
                ev_val = self.view.camera.center
            else:
                ev_val = self.view.camera._event_value
            dist = p2 #/ norm * self.view.camera._scale_factor

            dist[1] *= -1
            # Black magic part 1: turn 2D into 3D translations
            dx, dy, dz = self.view.camera._dist_to_trans(dist)
            # Black magic part 2: take up-vector and flipping into account
            ff = self.view.camera._flip_factors
            up, forward, right = self.view.camera._get_dim_vectors()
            dx, dy, dz = right * dx + forward * dy + up * dz
            dx, dy, dz = ff[0] * dx, ff[1] * dy, dz * ff[2]
            c = ev_val
            #shift by scale_factor half
            sc_half = self.view.camera._scale_factor/2
            point = c[0] + dx-sc_half, c[1] + dy-sc_half, c[2] + dz+sc_half
            print("final point:", point[0], point[1], point[2])


Scatter3D = scene.visuals.create_visual_node(visuals.MarkersVisual)
canvas = Canvas()

f = File("../../las_data/OnSnow_cliffs.las", mode = "r")

x = f.x
print(np.average(x))
y = f.y
print(np.average(y))
z = f.z 
print(np.average(z))
xyz = np.transpose(np.stack((x, y, z)))

p1 = Scatter3D(parent=canvas.view.scene)
p1.set_gl_state('translucent', blend=True, depth_test=True)

# fake data
# x = np.random.rand(100) * 10
# y = np.random.rand(100) * 10
# z = np.random.rand(100) * 10

# Draw it
point_list = [x, y, z]
point = np.array(point_list).transpose()
p1.set_data(xyz, symbol='o', size=6, edge_width=0.5, edge_color='blue')

if __name__ == "__main__":

    if sys.flags.interactive != 1:
        app.run()