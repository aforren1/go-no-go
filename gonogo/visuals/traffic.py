
from timeit import default_timer
import numpy as np

from pkg_resources import resource_filename

from mglg.graphics.shaders import FlatShader
from mglg.graphics.shape2d import Circle
from mglg.graphics.object import Object2D
from mglg.math.vector import Vector2f


class Traffic(object):

    def __init__(self, win, num=4, position=(0, 0), scale=(1, 1)):
        flat_shader = FlatShader(win.context)
        self.counter = 0
        self.num = num

        self.circs = []
        #
        for i in range(num):
            self.circs.append(Circle(win.context, flat_shader, is_outlined=False))

        self.position = Vector2f(position)
        self.scale = Vector2f(scale)

        self.reset_pos()
        self.reset()
        # subscales are scale/(1.5 * num)
        # offsets are np.linspace(-scale/2, scale/2, num) for x relative to position

    def reset_pos(self):
        # TODO: currently assumes scale never changes
        sd2 = self.scale[0]/2
        num = self.num
        self.offsets = np.linspace(-sd2, sd2, num)  # x offset
        self.subscales = self.scale[0]/(1.1 * num)
        for counter, i in enumerate(self.circs):
            i.position = self.position[0] + self.offsets[counter], self.position[1]
            i.scale = self.subscales

    def reset(self):
        self.counter = 0
        for i in self.circs:
            i.fill_color = (0.9, 0.2, 0.2, 1)

    def next(self):
        if self.counter >= len(self.circs):
            self.counter = 0
            return
        self.circs[self.counter].fill_color = (0.2, 0.9, 0.3, 1)
        self.counter += 1

    def draw(self, cam):
        for i in self.circs:
            i.draw(cam)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if isinstance(value, Vector2f):
            self._position = value
        else:
            self._position[:] = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        if isinstance(value, Vector2f):
            self._scale = value
        else:
            self._scale[:] = value
