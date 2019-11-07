import imgui
from imgui import (WINDOW_NO_COLLAPSE, WINDOW_NO_RESIZE, WINDOW_NO_TITLE_BAR)
from gonogo.visuals.imgui_abstractions import ProgrammablePygletRenderer
import numpy as np


class OnlinePlot(object):
    def __init__(self):
        self.flags = WINDOW_NO_COLLAPSE | WINDOW_NO_RESIZE | WINDOW_NO_TITLE_BAR
        self.photo = None
        self.l_button = None
        self.r_button = None
        self.l_force = None
        self.r_force = None

    def update(self, data):
        if data.any():
            if self.photo is None:
                # start new thing
                self.photo = data.photo
                self.l_button = data.buttons[:, 0]
                self.r_button = data.buttons[:, 1]
                self.l_force = data.forces[:, 0]
                self.r_force = data.forces[:, 1]
            elif max(self.photo.shape) < 1000:
                self.photo = np.hstack((self.photo, data.photo))
                self.l_button = np.hstack((self.l_button, data.buttons[:, 0]))
                self.r_button = np.hstack((self.r_button, data.buttons[:, 1]))
                self.l_force = np.hstack((self.l_force, data.forces[:, 0]))
                self.r_force = np.hstack((self.r_force, data.forces[:, 1]))
            else:
                shp = -data.photo.shape[0]
                self.photo = np.roll(self.photo, shp)
                self.l_button = np.roll(self.l_button, shp)
                self.r_button = np.roll(self.r_button, shp)
                self.l_force = np.roll(self.l_force, shp)
                self.r_force = np.roll(self.r_force, shp)

                self.photo[shp:] = data.photo
                self.l_button[shp:] = data.buttons[:, 0]
                self.r_button[shp:] = data.buttons[:, 1]
                self.l_force[shp:] = data.forces[:, 0]
                self.r_force[shp:] = data.forces[:, 1]

            imgui.set_next_window_size(270, 600)
            imgui.begin('plot', False, self.flags)
            imgui.plot_lines('Photo', self.photo.astype('f')/2**10,
                             scale_min=0, scale_max=1, graph_size=(180, 100))
            imgui.plot_lines('l_force', self.l_force.astype('f')/2**12,
                             scale_min=0, scale_max=1, graph_size=(180, 100))
            imgui.plot_lines('r_force', self.r_force.astype('f')/2**12,
                             scale_min=0, scale_max=1, graph_size=(180, 100))
            style = imgui.get_style()
            imgui.plot_lines('l_button', smooth(self.l_button.astype('f')) * 6,
                             scale_min=-1.1, scale_max=1.1, graph_size=(180, 100))
            imgui.plot_lines('r_button', smooth(self.r_button.astype('f')) * 6,
                             scale_min=-1.1, scale_max=1.1, graph_size=(180, 100))
            imgui.end()


def smooth(x, window_len=11):
    s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
    # print(len(s))
    w = np.ones(window_len, 'f')
    y = np.convolve(w/w.sum(), s, mode='valid')
    return y
