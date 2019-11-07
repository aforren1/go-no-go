import moderngl as mgl
import numpy as np

from mglg.graphics.drawable import Drawable2D
from mglg.graphics.camera import Camera
from gonogo.visuals.projection import height_ortho
from mglg.math.vector import Vector4f


class RenderSurface2D(Drawable2D):
    vao = None

    def __init__(self, context, shader, alpha=1.0, clear_color=(0.3, 0.3, 0.3, 1.0), *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        self.context = context
        self.cam = Camera(projection=height_ortho(self.scale.x, self.scale.y))

        self.texture = context.texture(context.screen.size, 4)
        self.fbo = context.framebuffer(self.texture)  # TODO: do we need depth attachment??

        self.clear_color = Vector4f(clear_color)
        self.alpha = alpha

        if self.vao is None:
            vertex_texcoord = np.zeros(4, dtype=[('vertices', np.float32, 3),
                                                 ('texcoord', np.float32, 2)])
            vertex_texcoord['vertices'] = [(-0.5, -0.5, 0), (0.5, -0.5, 0),
                                           (-0.5, 0.5, 0), (0.5, 0.5, 0)]
            vertex_texcoord['texcoord'] = [(0, 0), (1, 0),
                                           (0, 1), (1, 1)]
            vbo = context.buffer(vertex_texcoord.view(np.ubyte))
            self.set_vao(context, shader, vbo)

    def use(self):
        self.fbo.clear(*self.clear_color)
        self.fbo.use()

    def unuse(self):
        self.context.screen.use()

    def __enter__(self):
        self.use()
        return self

    def __exit__(self, *args):
        self.unuse()

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.shader['alpha'].value = self.alpha
            self.texture.use()
            self.vao.render(mgl.TRIANGLE_STRIP)

    @classmethod
    def set_vao(cls, context, shader, vbo):
        # re-use VAO
        cls.vao = context.simple_vertex_array(shader, vbo, 'vertices', 'texcoord')

    @property
    def clear_color(self):
        return self._clear_color

    @clear_color.setter
    def clear_color(self, color):
        if isinstance(color, Vector4f):
            self._clear_color = color
        else:
            self._clear_color[:] = color


if __name__ == '__main__':
    from mglg.graphics.shaders import FlatShader, ImageShader
    from gonogo.visuals.window import ExpWindow as Win
    from mglg.graphics.shape2d import Arrow

    win = Win(background_color=(0.7, 0.6, 0.5, 1))
    flat = FlatShader(win.context)
    image = ImageShader(win.context)

    render_surf = RenderSurface2D(win.context, image, alpha=0.8,
                                  scale=(5/6, 3/5), position=(1/4, 1/6-0.03))

    arrow = Arrow(win.context, flat, scale=(0.1, 0.1), fill_color=(0, 0.2, 1, 1), position=(0.4, 0.4))

    counter = 0
    while True:
        counter += 1
        arrow.position.x = np.sin(counter/60)/2
        arrow.position.y = np.cos(counter/81)/2
        arrow.rotation += 2
        with render_surf:
            arrow.draw(render_surf.cam)
        arrow.draw(win.cam)
        render_surf.draw(win.cam)
        win.flip()
        if win.dt > 0.2:
            print(win.dt)
