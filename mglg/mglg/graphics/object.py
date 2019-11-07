from math import cos, sin
from numpy import pi, float32, eye
from mglg.math.vector import Vector2f


class Object2D(object):
    def __init__(self, position=(0, 0), rotation=0, scale=(1, 1), *args, **kwargs):
        self.position = Vector2f(position)
        self.rotation = rotation
        self.scale = Vector2f(scale)
        self._model_matrix = eye(4, dtype=float32)

    @property
    def model_matrix(self):
        # TODO: any caching?
        mm = self._model_matrix
        make_2d_mm(self.position, self.rotation, self.scale, mm)
        return mm

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


def make_2d_mm(pos, rot, scal, out):
    # this beats np.radians, and imul seems slower than *
    rot = rot * (pi/180.0)
    # this beats np.cos(..., dtype=np.float32)
    s = float32(sin(rot))
    c = float32(cos(rot))
    out[0, 0] = scal[0] * c
    out[0, 1] = s * scal[0]
    out[1, 0] = -s * scal[1]  # pylint: disable=invalid-unary-operand-type
    out[1, 1] = scal[1] * c
    out[2, 2] = 1.0
    out[3, 0] = pos[0]
    out[3, 1] = pos[1]
    out[3, 3] = 1.0


if __name__ == '__main__':
    from mglg.util import timethat
    import numpy as np

    out = np.eye(4, dtype=np.float32)

    pos = (0, 0)
    rot = 34.0
    scal = (1, 1)

    # first, look at perf with
    setup = 'from __main__ import make_2d_mm, pos, rot, scal, out'
    timethat('make_2d_mm(pos, rot, scal, out)', setup=setup)

    # next, non-matching types
    pos = np.array(pos)
    scal = np.array(scal)
    timethat('make_2d_mm(pos, rot, scal, out)', setup=setup)

    # match types
    pos = pos.astype(np.float32)
    scal = scal.astype(np.float32)
    timethat('make_2d_mm(pos, rot, scal, out)', setup=setup)

    obj = Object2D()
    setup2 = 'from __main__ import obj'
    timethat('obj.model_matrix', setup=setup2)
