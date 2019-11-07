import numpy as np

import moderngl as mgl
from mglg.graphics.drawable import Drawable2D
from mglg.graphics.shape2d import _make_2d_indexed
from mglg.graphics.shape2d import square_vertices, line_vertices, arrow_vertices, circle_vertices
from mglg.math.vector import Vector4f
from mglg.graphics.camera import Camera


class Stipple2D(Drawable2D):
    def __init__(self, context, shader,
                 width, height, vertices=None,
                 pattern=0xff00, color=(1, 1, 1, 1),
                 *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)

        if not hasattr(self, '_vertices'):
            self._vertices, _ = _make_2d_indexed(vertices)

        vbo = context.buffer(self._vertices.view(np.ubyte))
        self.vao = context.simple_vertex_array(shader, vbo, 'vertices')
        self.color = Vector4f(color)
        self.window_dims = width, height
        self.pattern = pattern
        shader['u_resolution'].value = width, height
        shader['u_factor'].value = 2.0
        shader['u_pattern'].value = pattern

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.shader['color'].write(self.color._ubyte_view)
            self.vao.render(mgl.LINE_LOOP)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, Vector4f):
            self._color = color
        else:
            self._color[:] = color


class StippleSquare(Stipple2D):
    _vertices, _ = _make_2d_indexed(square_vertices)
    # TODO: squish vertices kwarg


class StippleLine(Stipple2D):
    _vertices, _ = _make_2d_indexed(line_vertices)


class StippleArrow(Stipple2D):
    _vertices, _ = _make_2d_indexed(arrow_vertices)


class StippleCircle(Stipple2D):
    _vertices, _ = _make_2d_indexed(circle_vertices)
