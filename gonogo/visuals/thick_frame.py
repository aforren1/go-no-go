import numpy as np
import moderngl as mgl

from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D

from mglg.math.vector import Vector4f


class ThickFrame(Drawable2D):
    def __init__(self, context, shader, color=[0.2, 0.2, 0.2, 1],
                 *args, **kwargs):
        super().__init__(context, shader, **kwargs)
        self.color = Vector4f(color)

        verts = [[-0.5, -0.5], [-0.45, -0.45], [-0.5, 0.5], [-0.45, 0.45],
                 [0.5, 0.5], [0.45, 0.45], [0.5, -0.5], [0.45, -0.45],
                 [-0.5, -0.5], [-0.45, -0.45]]
        vertices = np.zeros((10, 3), dtype=np.float32)

        vertices[:, :2] = verts
        vertices = vertices.ravel().view(np.ubyte)
        vert_vbo = context.buffer(vertices)

        self.vao = context.vertex_array(shader, [(vert_vbo, '3f', 'vertices')])

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.shader['color'].write(self.color._ubyte_view)
            self.vao.render(mgl.TRIANGLE_STRIP)

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
    from mglg.graphics.shaders import FlatShader
    from gonogo.visuals.window import ExpWindow as Win

    win = Win()
    flat = FlatShader(win.context)
    thick_frame = ThickFrame(win.context, flat, color=(0.2, 0.3, 0.8, 1), scale=(0.25, 0.4))
    for i in range(100):
        thick_frame.rotation += 3
        thick_frame.draw(win.cam)
        win.flip()
