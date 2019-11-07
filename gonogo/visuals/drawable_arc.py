import numpy as np
import moderngl as mgl

from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D
from mglg.math.vector import Vector4f
from mglg.graphics.shape2d import _make_2d_indexed

# semicircle from pi to 2*pi
# (bottom half, 'cause that's all we're using)


def make_arc(start=np.pi, stop=2*np.pi, segments=181, factor=0.5):
    lx = np.linspace(start, stop, segments, dtype=np.float32)
    vertices = np.zeros((segments, 2), dtype=np.float32)
    vertices[:, 0] = np.cos(lx)
    vertices[:, 1] = np.sin(lx)
    return vertices * factor


class DrawableArc(Drawable2D):
    def __init__(self, context, shader,
                 left_color=[1]*4, right_color=[0, 0, 0, 1],
                 angle=90, *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        # notes: each vertex corresponds to one degree
        # pre-bake these for now so we don't need to bother w/ generalization
        start = np.pi
        stop = 2*np.pi
        segments = 181
        vertices = np.zeros((segments, 4), dtype=np.float32)
        vertices[:, :2] = make_arc(start, stop, segments, factor=0.5)

        vert_vbo = context.buffer(vertices.ravel().view(np.ubyte))

        # initialize color buffer (which is dynamic & per-vertex)
        # TODO: should we do integers? 8 bits per channel is def enough
        self.left_color = Vector4f(left_color)
        self.right_color = Vector4f(right_color)
        self._colors = np.zeros(segments, dtype=[('color', np.float32, 4)])
        self._colors['color'][:angle] = left_color
        self._colors['color'][angle] = (1, 1, 1, 1)
        self._colors['color'][(angle + 1):] = right_color
        self._angle = self._pending_angle = angle
        self._dirty_angle = False

        self._color_vbo = context.buffer(self._colors.view(np.ubyte), dynamic=True)

        self.vao = context.vertex_array(shader,
                                        [
                                            (vert_vbo, '4f', 'vertices'),
                                            (self._color_vbo, '4f', 'color')
                                        ])

    def draw(self, camera: Camera):
        if self.visible:
            if self._angle != self._pending_angle:
                self.update_arc_color(self._pending_angle)
                self._color_vbo.write(self._delta_view, offset=self._offset)
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.vao.render(mgl.LINE_STRIP)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._pending_angle = value

    def update_arc_color(self, new_angle):
        # updates the arc color & then finally sets the pending angle
        old_angle = self._angle
        delta = new_angle - old_angle  # tells us which way to stride
        if delta > 0:  # moving division to the right (CCW)
            self._colors['color'][old_angle:new_angle] = self.left_color
            self._colors['color'][new_angle] = (1, 1, 1, 1)
            slc = slice(old_angle, new_angle+1, None)
        else:  # moving division to the left (CW)
            self._colors['color'][(new_angle + 1):(old_angle + 1)] = self.right_color
            self._colors['color'][new_angle] = (1, 1, 1, 1)
            slc = slice(new_angle, old_angle+1, None)
        # dirty section + offset
        self._delta_view = self._colors[slc].view(np.ubyte)
        self._offset = slc.start * 16  # index * size of a single thing in bytes
        self._angle = new_angle


class ThickDivArc(Drawable2D):
    def __init__(self, context, shader, left_color=(230/255, 159/255, 0, 1),
                 right_color=(0, 114/255, 178/255, 1), angle=90,
                 radius=0.5, thickness=0.1, *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        self.left_color = Vector4f(left_color)
        self.right_color = Vector4f(right_color)
        self._start = np.pi
        self._stop = 2*np.pi
        self._old_angle = angle
        self._angle = angle
        self._radius = radius
        self._thickness = thickness
        _vertices = np.zeros(3602, dtype=[('vertices', np.float32, 3)])
        self._vertices = _vertices
        # 1810*2 vertices, (x,y,z), 4 bytes per
        self.vert_vbo = context.buffer(_vertices.view(np.ubyte), dynamic=True)
        # 1810*2 vertices, (r,g,b,a), 4 bytes per
        _colors = np.zeros(3602, dtype=[('color', np.float32, 4)])
        angle2 = int(angle * 10*2)
        _colors['color'][:angle2] = left_color
        _colors['color'][angle2:(angle2 + 2)] = (1, 1, 1, 1)
        _colors['color'][(angle2 + 2):] = right_color
        self._colors = _colors
        self.color_vbo = context.buffer(_colors.view(np.ubyte), dynamic=True)

        self.vao = context.vertex_array(shader,
                                        [
                                            (self.vert_vbo, '3f', 'vertices'),
                                            (self.color_vbo, '4f', 'color')
                                        ])
        # should be a combo of ThickArc and DrawableArc
        # vertices are dynamic so we can keep thickness const with changing scale,
        # colors are dynamic so we can change colors
        self._recalc_vertices()
        self._recalc_colors()
        self._need_new_colors = False
        self._need_new_vertices = False

    def draw(self, camera: Camera):
        if self.visible:
            if self._need_new_vertices:  # changed radius, need to recalculate
                self._recalc_vertices()
                self._need_new_vertices = False
            if self._need_new_colors:  # changed the angle, need to recalculate colors
                self._recalc_colors()
                self._need_new_colors = False
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.vao.render(mgl.TRIANGLE_STRIP)

    def _recalc_vertices(self):
        # this is fairly expensive? we re-send *all* vertices
        # 1/10 angle resolution
        inner = make_arc(start=self._start, stop=self._stop,
                         segments=1801, factor=(self.radius/2) - (self.thickness/2))
        outer = make_arc(start=self._start, stop=self._stop,
                         segments=1801, factor=(self.radius/2) + (self.thickness/2))
        # z is zero
        # we do a little useless work here (z never changes in our experiment)
        # and we *could* just write x and y
        self._vertices['vertices'][::2, :2] = inner
        self._vertices['vertices'][1::2, :2] = outer
        self.vert_vbo.write(self._vertices.view(np.ubyte))

    def _recalc_colors(self):
        delta = self._angle - self._old_angle
        old2 = int(self._old_angle * 10 * 2)
        new2 = int(self._angle * 10 * 2)
        if delta > 0:  # divider moving to right (CCW)
            self._colors['color'][old2:new2] = self.left_color
            self._colors['color'][new2:(new2+2)] = (1, 1, 1, 1)
            slc = slice(old2, new2+2, None)
        else:  # divider moving to left (CW)
            self._colors['color'][new2:(new2+2)] = (1, 1, 1, 1)
            self._colors['color'][(new2 + 2):(old2 + 2)] = self.right_color
            slc = slice(new2, old2+2, None)
        delta_view = self._colors[slc].view(np.ubyte)
        offset = slc.start * 16
        self.color_vbo.write(delta_view, offset=offset)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if self._angle == value:
            return
        self._old_angle = self._angle
        self._angle = value
        self._need_new_colors = True

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if self._radius == value:
            return
        self._radius = value
        self._need_new_vertices = True

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        if self._thickness == value:
            return
        self._thickness = value
        self._need_new_vertices = True

    @property
    def left_color(self):
        return self._left_color

    @left_color.setter
    def left_color(self, color):
        if isinstance(color, Vector4f):
            self._left_color = color
        else:
            self._left_color[:] = color

    @property
    def right_color(self):
        return self._right_color

    @right_color.setter
    def right_color(self, color):
        if isinstance(color, Vector4f):
            self._right_color = color
        else:
            self._right_color[:] = color


class ThickArc(Drawable2D):

    def __init__(self, context: mgl.Context, shader,
                 radius=0.5, thickness=0.1, color=(1, 1, 1, 1),
                 *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        self._need_recalc = True
        self.context = context
        self._radius = radius
        self._thickness = None
        self.thickness = thickness
        self.color = Vector4f(color)

    def draw(self, camera: Camera):
        if self.visible:
            # do pending calc
            if self._need_recalc:
                self._recalc_vertices()
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.shader['color'].write(self.color._ubyte_view)
            self.vao.render(mgl.TRIANGLE_STRIP_ADJACENCY)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if self._radius == value:
            return
        self._radius = value
        self._need_recalc = True

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        # re-calculate vertices (if needed)
        if self._thickness == value:
            return
        self._thickness = value
        self._need_recalc = True

    def _recalc_vertices(self):
        # inner arc
        self._need_recalc = False
        inner = make_arc(start=-np.pi/4, stop=np.pi/4, segments=60, factor=(self.radius/2) - (self.thickness / 2))
        outer = make_arc(start=-np.pi/4, stop=np.pi/4, segments=60, factor=(self.radius/2) + (self.thickness / 2))
        new_vertices = np.zeros((inner.shape[0] * 2, 2), dtype=np.float32)
        new_vertices[::2] = inner
        new_vertices[1::2] = outer
        vert_b = new_vertices.view(np.ubyte)
        # initialize
        if not hasattr(self, 'vert_vbo'):
            self.vert_vbo = self.context.buffer(vert_b, dynamic=True)
            self.vao = self.context.simple_vertex_array(self.shader, self.vert_vbo, 'vertices')
        else:  # update buffer
            self.vert_vbo.write(vert_b)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, Vector4f):
            self._color = color
        else:
            self._color[:] = color


if __name__ == '__main__':
    from mglg.graphics.shaders import FlatShader, VertexColorShader
    from mglg.graphics.shape2d import Square
    from gonogo.visuals.window import ExpWindow as Win

    win = Win()
    flat = FlatShader(win.context)
    vcs = VertexColorShader(win.context)
    # don't touch scale
    arc4 = ThickDivArc(win.context, vcs, radius=0.9, angle=90)
    sqr = Square(win.context, flat, scale=(0.0005, 2))
    sqr2 = Square(win.context, flat, scale=(2, 0.0005))
    for i in range(180):
        #arc4.angle += 1
        sqr.draw(win.cam)
        sqr2.draw(win.cam)
        arc4.draw(win.cam)
        win.flip()
