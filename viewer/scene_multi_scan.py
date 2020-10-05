"""
    3D Points Picking & select tool based on Vispy library
    Author: Penny Xuran Qian (NAOC/SAO) pennyqxr@gmail.com
    Controls:
    * 1 - free lasso select
    * 2 - rectangle select
    * 3 - ellipse select
    * 4 - point picking
    press again to switch between select and view mode
"""

import sys
import numpy as np
import copy

from PyQt5 import QtWidgets, QtCore, QtGui
from vispy import scene
from matplotlib import path
from laspy.file import File


def rectangle_vertice(center, height, width):
    # Borrow from _generate_vertices in vispy/visuals/rectangle.py

    half_height = height / 2.
    half_width = width / 2.

    bias1 = np.ones(4) * half_width
    bias2 = np.ones(4) * half_height

    corner1 = np.empty([1, 3], dtype=np.float32)
    corner2 = np.empty([1, 3], dtype=np.float32)
    corner3 = np.empty([1, 3], dtype=np.float32)
    corner4 = np.empty([1, 3], dtype=np.float32)

    corner1[:, 0] = center[0] - bias1[0]
    corner1[:, 1] = center[1] - bias2[0]
    corner1[:, 2] = 0

    corner2[:, 0] = center[0] + bias1[1]
    corner2[:, 1] = center[1] - bias2[1]
    corner2[:, 2] = 0

    corner3[:, 0] = center[0] + bias1[2]
    corner3[:, 1] = center[1] + bias2[2]
    corner3[:, 2] = 0

    corner4[:, 0] = center[0] - bias1[3]
    corner4[:, 1] = center[1] + bias2[3]
    corner4[:, 2] = 0

    # Get vertices between each corner of the rectangle for border drawing
    vertices = np.concatenate(([[center[0], center[1], 0.]],
                               [[center[0] - half_width, center[1], 0.]],
                               corner1,
                               [[center[0], center[1] - half_height, 0.]],
                               corner2,
                               [[center[0] + half_width, center[1], 0.]],
                               corner3,
                               [[center[0], center[1] + half_height, 0.]],
                               corner4,
                               [[center[0] - half_width, center[1], 0.]]))

    # vertices = np.array(output, dtype=np.float32)
    return vertices[1:, ..., :2]

"""
def ellipse_vertice(center, radius, start_angle, span_angle, num_segments):
    # Borrow from _generate_vertices in vispy/visual/ellipse.py

    if isinstance(radius, (list, tuple)):
        if len(radius) == 2:
            xr, yr = radius
        else:
            raise ValueError("radius must be float or 2 value tuple/list"
                             " (got %s of length %d)" % (type(radius),
                                                         len(radius)))
    else:
        xr = yr = radius

    start_angle = np.deg2rad(start_angle)

    # Segment as 1000
    vertices = np.empty([num_segments + 2, 2], dtype=np.float32)

    # split the total angle as num segments
    theta = np.linspace(start_angle,
                        start_angle + np.deg2rad(span_angle),
                        num_segments + 1)

    # PolarProjection
    vertices[:-1, 0] = center[0] + xr * np.cos(theta)
    vertices[:-1, 1] = center[1] + yr * np.sin(theta)

    # close the curve
    vertices[num_segments + 1] = np.float32([center[0], center[1]])

    return vertices[:-1]

"""
class Multi_Scene(QtWidgets.QWidget):
    def __init__(self, points, color, scene_type, keys='interactive'):
        super(Multi_Scene, self).__init__()
        # Layout and canvas creation
        box = QtWidgets.QVBoxLayout(self)
        self.scene_type = scene_type
        print('scene type', scene_type)
        self.setLayout(box)
        self.canvas = scene.SceneCanvas(keys=keys)
        box.addWidget(self.canvas.native)


        # Connect events
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        self.canvas.events.mouse_release.connect(self.on_mouse_release)
        self.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.canvas.events.key_press.connect(self.on_key_press)

        # Setup some defaults
        self.mesh = None
        self.selected = []

        # Data
        self.data = points
        avg_x = 0
        avg_y = 0
        avg_z = 0
        for data in self.data:
            avg_x += np.average(data[:,0])
            avg_y += np.average(data[:,1])
            avg_z += np.average(data[:,2])

        avg_x /= len(self.data)
        avg_y /= len(self.data)
        avg_z /= len(self.data)
        
        # Color
        self.base_facecolor = copy.deepcopy(color)
        self.facecolor = copy.deepcopy(color)
        
        # Camera
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(#fov=45,
        elevation=-np.arctan(avg_z/avg_x)*360,
        azimuth=np.arctan(avg_y/avg_x)*360,
        roll=np.arctan(avg_z/avg_y)*360,
        distance=np.sqrt(avg_x**2+avg_y**2+avg_z**2),
        center=(avg_x, avg_y, avg_z))

        # Add Plot
        self.scatter = []
        self.base_facecolor = copy.deepcopy(color)
        self.facecolor = copy.deepcopy(color)
        self.ptsize = 3
        for i in range(len(self.data)):
            data = self.data[i]
            color = self.facecolor[i]
            scatter = scene.visuals.Markers()
            scatter.set_data(data, face_color=color,
                                edge_color=None, size=self.ptsize)
            self.view.add(scatter)
            self.scatter.append(scatter)

        font_size = 20.0
        # Add a text instruction
        self.text = scene.visuals.Text('', pos=(self.canvas.size[0],  20),
                                       color='w', parent=self.canvas.scene)
        self.stats_text = scene.visuals.Text('', pos=(self.canvas.size[0]/4.0,  int(font_size*1.33)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.stats_text2 = scene.visuals.Text('', pos=(self.canvas.size[0]/4.0,  int(font_size*1.33*2+font_size*1.33*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.stats_text3 = scene.visuals.Text('', pos=(self.canvas.size[0]/4.0,  int(font_size*1.33*3+font_size*1.33*2*0.5)),
                                       color='w', bold = True, font_size = font_size, parent=self.canvas.scene)
        self.tr = self.scatter[0].node_transform(self.view)

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        # Set up for lasso drawing
        self.line_pos = []
        self.line = scene.visuals.Line(color='white', method='gl',
                                       parent=self.canvas.scene)

        # select
        self.select_flag = False
        self.select_pool = {'1': 'lasso', '2': 'rectangle'}
        self.select_id = '2'  # default as 2
        self.select_origin = (0, 0)

    def event_connect(self, flag):
        cam_events = self.view.camera._viewbox.events
        cam_mouse_event = self.view.camera.viewbox_mouse_event
        if flag:
            cam_events.mouse_move.disconnect(cam_mouse_event)
            cam_events.mouse_press.disconnect(cam_mouse_event)
            cam_events.mouse_release.disconnect(cam_mouse_event)
            cam_events.mouse_wheel.disconnect(cam_mouse_event)
        else:
            cam_events.mouse_move.connect(cam_mouse_event)
            cam_events.mouse_press.connect(cam_mouse_event)
            cam_events.mouse_release.connect(cam_mouse_event)
            cam_events.mouse_wheel.connect(cam_mouse_event)

    def mark_selected(self, i):
        # i is the index reference
        # Change the color of the selected point
        self.facecolor[i] = copy.deepcopy(self.base_facecolor[i])

        self.scatter[i].set_data(self.data[i], face_color=self.facecolor[i],
                              size=self.ptsize)

        for j in self.selected[i]:
            self.facecolor[i][j] = [1.0, 0.0, 1.0]


        self.scatter[i].set_data(self.data[i], face_color=self.facecolor[i],
                              size=self.ptsize)
        self.scatter[i].update()

        if self.scene_type == 'Depth':
            if len(self.data[i][tuple(self.selected)]) > 0 and self.grid.snow_depth_key != None:
                stats = self.grid.get_stats(self.data[i][tuple(self.selected)]) 

                # add call to get snowdepth here
                # get average x,y,z
                self.stats_text.text = str(f'Average Depth: {stats[0]}')
                self.stats_text2.text = str(f'Max Depth: {stats[1]}')
                self.stats_text3.text = str(f'Min Depth: {stats[2]}')
            else:
                self.stats_text.text = str(f'Average Depth: n/a')
                self.stats_text2.text = str(f'Max Depth: n/a')
                self.stats_text3.text = str(f'Min Depth: n/a')

        if self.scene_type == 'ICP':
            pass

    def permanently_mark_selected(self):
        for i in range(len(self.selected)):
            for j in self.selected[i]:
                self.base_facecolor[i][j]= [1.0, 1.0, 1.0]
            self.scatter[i].set_data(self.data[i], face_color=self.base_facecolor[i],
                                size=self.ptsize)
            self.scatter[i].update()

    def remove_selected_points(self):#, removal_points):
        for i in self.selected:
            if len(self.selected[i]) > 0:
                self.data[i] = self.data[i][tuple(np.invert(self.selected[i]))]
                self.base_facecolor[i] = self.base_facecolor[i][tuple(np.invert(self.selected[i]))]
                self.facecolor[i] = copy.deepcopy(self.base_facecolor[i])
                self.scatter[i].set_data(self.data[i], face_color=self.facecolor[i],
                                    size=self.ptsize)
                self.scatter[i].update()
                self.selected[i] = []
        return self.data

    def on_key_press(self, event):
        # Set select_flag and instruction text

        if event.text == '1': #in self.select_pool.keys():
            if self.select_flag:
                if self.select_id == '2':
                    self.select_id = '1'
                    self.text.text = 'In lasso select mode, press 1 to switch to rectangular select'
                else:
                    self.select_id = '2'
                    self.text.text = 'In rectangular select mode, press 1 to switch to lasso select'
                                 

    def on_mouse_press(self, event):
        # Realize picking functionality and set origin mouse pos
        
        if event.button == 1 and self.select_flag:
            self.select_origin = event.pos

    def on_mouse_release(self, event):
        # Identify selected points and mark them

        if event.button == 1 and self.select_flag:
            self.selected = []
            for i in range(len(self.data)):
                self.facecolor[i] = self.base_facecolor[i]
                data = self.tr.map(self.data[i])[:, :2]

                self.selected.append([])
                select_path = path.Path(self.line_pos, closed=True)
                mask = [select_path.contains_points(data)]

                # if len(self.data[tuple(mask)]) > 0:
                self.selected[i] = mask
                self.mark_selected(i)

            # Reset lasso
            # TODO: Empty pos input is not allowed for line_visual
            self.line_pos = []
            self.line.set_data(np.array(self.line_pos))
            self.line.update()

            if self.select_id == '2':
                self.select_origin = None

    def on_mouse_move(self, event):
        # Draw lasso/rectangle/ellipse shape with mouse dragging

        if event.button == 1 and event.is_dragging and self.select_flag:
            if self.select_id == '1':
                self.line_pos.append(event.pos)
                self.line.set_data(np.array(self.line_pos))

            if self.select_id == '2':
                width = event.pos[0] - self.select_origin[0]
                height = event.pos[1] - self.select_origin[1]
                center = (width/2. + self.select_origin[0],
                          height/2.+self.select_origin[1], 0)
                self.line_pos = rectangle_vertice(center, height, width)
                self.line.set_data(np.array(self.line_pos))

# if __name__ == '__main__':
#     appQt = QtWidgets.QApplication(sys.argv)
#     view = DemoScene(keys='interactive')
#     view.show()
#     appQt.exec_()