from button_actions import *
from PyQt5 import QtWidgets, QtCore, QtGui
import vispy.app
import sys
from grid import Grid
from data_manager import Manager, file_object
import numpy as np
# from window import Window

class Canvas(vispy.app.Canvas):
    # resize = pyqtSignal()
    def __init__(self):
        super(Canvas, self).__init__()
        # self.resize.connect(self.resize_widgets())
        # self.window = Window()

    def set_canvas_to_grid(self):
        return self

    # def on_mouse_press(self, event):
    #     # if True:
    #         #1=left, 2=right , 3=middle button
    #         # if event.button == 1:
    #     p2 = event.pos
    #     norm = np.mean(self.window.plot_widgets.widget[0].view.camera._viewbox.size)

    #     if self.window.plot_widgets.widget[0].view.camera._event_value is None or len(self.window.plot_widgets.widget[0].view.camera._event_value) == 2:
    #         ev_val = self.window.plot_widgets.widget[0].view.camera.center
    #     else:
    #         ev_val = self.window.plot_widgets.widget[0].view.camera._event_value
    #     dist = p2 / norm * self.window.plot_widgets.widget[0].view.camera._scale_factor

    #     dist[1] *= -1
    #     # Black magic part 1: turn 2D into 3D translations
    #     dx, dy, dz = self.window.plot_widgets.widget[0].view.camera._dist_to_trans(dist)
    #     # Black magic part 2: take up-vector and flipping into account
    #     ff = self.window.plot_widgets.widget[0].view.camera._flip_factors
    #     up, forward, right = self.window.plot_widgets.widget[0].view.camera._get_dim_vectors()
    #     dx, dy, dz = right * dx + forward * dy + up * dz
    #     dx, dy, dz = ff[0] * dx, ff[1] * dy, dz * ff[2]
    #     c = ev_val
    #     #shift by scale_factor half
    #     sc_half = self.window.plot_widgets.widget[0].view.camera._scale_factor/2
    #     point = c[0] + dx-sc_half, c[1] + dy-sc_half, c[2] + dz+sc_half
    #     print("final point:", point[0], point[1], point[2])