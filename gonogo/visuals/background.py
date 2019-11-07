import numpy as np
import moderngl as mgl

from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D

from mglg.math.vector import Vector4f


class Background(Drawable2D):
    def __init__(self, context, shader,
                 base_color=[0.3, 0.3, 0.3, 1],
                 detail_color=[0.9, 0.2, 0.2, 1], *args, **kwargs):
        super().__init__(context, shader, **kwargs)

        verts = [[-0.5, -0.5], [-0.35, -0.5], [-0.5, -0.35], [-0.35, -0.35], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]
        indices = [0, 1, 2, 1, 2, 3,  # inner
                   1, 3, 4, 3, 4, 5, 3, 5, 6, 6, 3, 2]
        indices = context.buffer(np.array(indices, dtype=np.int32))
        vertices = np.zeros((7, 3), dtype=np.float32)
        vertices[:, :2] = verts
        vertices = vertices.ravel().view(np.ubyte)
        vert_vbo = context.buffer(vertices)
        self.base_color = Vector4f(base_color)
        self.detail_color = Vector4f(detail_color)
        colors = np.zeros(7, dtype=[('color', np.float32, 4)])
        colors['color'][1:] = self.base_color
        colors['color'][0] = self.detail_color
        color_vbo = context.buffer(colors.view(np.ubyte))

        self.vao = context.vertex_array(shader,
                                        [
                                            (vert_vbo, '3f', 'vertices'),
                                            (color_vbo, '4f', 'color')
                                        ], index_buffer=indices)

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.vao.render(mgl.TRIANGLES)


if __name__ == '__main__':
    from mglg.graphics.shaders import VertexColorShader
    from gonogo.visuals.window import ExpWindow as Win
    from time import sleep

    win = Win()
    per_vert = VertexColorShader(win.context)
    background = Background(win.context, per_vert, scale=(1.5, 1))
    while True:
        background.draw(win.cam)
        win.flip()
