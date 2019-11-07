import numpy as np
import moderngl as mgl

from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D
from mglg.math.vector import Vector4f


def make_fill_verts():
    # 100 pairs (200 total)
    out = np.zeros((200, 2), dtype=np.float32)
    out[:, 0] = np.repeat(np.arange(-0.5, 0.5, 1/100, dtype=np.float32), 2)
    out[::2, 1] = 0.05
    out[1::2, 1] = -0.05
    return out


class FillBar(Drawable2D):
    def __init__(self, context, shader,
                 fill_color=1, empty_color=[0, 0, 0, 1],
                 *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)

        vertices = np.zeros((200, 4), dtype=np.float32)
        vertices[:, :2] = make_fill_verts()
        vert_vbo = context.buffer(vertices.ravel().view(np.ubyte))
        self.fill_color = Vector4f(fill_color)
        self.empty_color = Vector4f(empty_color)
        self._colors = np.zeros(200, dtype=[('color', np.float32, 4)])
        self._colors['color'][:] = fill_color
        self._pending_percentage = self._percentage = self.percentage = 100
        self._dirty_percentage = False

        self._color_vbo = context.buffer(self._colors.view(np.ubyte), dynamic=True)
        self.vao = context.vertex_array(shader,
                                        [
                                            (vert_vbo, '4f', 'vertices'),
                                            (self._color_vbo, '4f', 'color')
                                        ])

    def draw(self, camera: Camera):
        if self.visible:
            if self._percentage != self._pending_percentage:
                self.update_fill_color(self._pending_percentage)
                self._color_vbo.write(self._delta_view, offset=self._offset)
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.vao.render(mgl.TRIANGLE_STRIP)

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        if value > 100 or value < 0:
            raise ValueError('Invalid percentage.')
        self._pending_percentage = int(value)

    def update_fill_color(self, new_percentage):
        old_percentage = self._percentage
        delta = new_percentage - old_percentage
        op2, np2 = old_percentage*2, new_percentage*2
        if delta > 0:  # moving division to right (filling up)
            self._colors['color'][op2:np2] = self.fill_color
            slc = slice(op2, np2, None)
        else:  # moving division to left (filling down)
            self._colors['color'][np2:op2 + 1] = self.empty_color
            slc = slice(np2, op2+1, None)
        self._delta_view = self._colors[slc].view(np.ubyte)
        self._offset = slc.start * 16
        self._percentage = new_percentage


if __name__ == '__main__':
    from mglg.graphics.shaders import VertexColorShader
    from gonogo.visuals.window import ExpWindow as Win
    from time import sleep

    win = Win()
    per_vert = VertexColorShader(win.context)
    fill_bar = FillBar(win.context, per_vert, fill_color=[0.3, 0.8, 0.2, 1],
                       empty_color=[0.2, 0.2, 0.2, 1], scale=1, rotation=90)
    for i in range(100):
        fill_bar.percentage -= 1
        fill_bar.draw(win.cam)
        win.flip()
    for i in range(100):
        fill_bar.percentage += 1
        fill_bar.draw(win.cam)
        win.flip()
    sleep(0.4)
