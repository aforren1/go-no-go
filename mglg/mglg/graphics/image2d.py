import numpy as np
from PIL import Image

import moderngl as mgl
from mglg.graphics.camera import Camera
from mglg.graphics.drawable import Drawable2D

# avoid making new textures if we already have the exact texture
texture_cache = {}


class Image2D(Drawable2D):
    vao = None

    def __init__(self, context, shader, image_path, alpha=1.0, *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        image = Image.open(image_path).convert('RGBA')
        img_bytes = image.tobytes()
        img_hash = hash(img_bytes)
        if img_hash in texture_cache.keys():
            self.texture = texture_cache[img_hash]
        else:
            self.texture = context.texture(image.size, 4, img_bytes)
            texture_cache[img_hash] = self.texture
        self.alpha = alpha

        if self.vao is None:
            vertex_texcoord = np.zeros(4, dtype=[('vertices', np.float32, 3),
                                                 ('texcoord', np.float32, 2)])
            vertex_texcoord['vertices'] = [(-0.5, -0.5, 0), (-0.5, 0.5, 0),
                                           (0.5, -0.5, 0), (0.5, 0.5, 0)]
            vertex_texcoord['texcoord'] = [(0, 1), (0, 0),
                                           (1, 1), (1, 0)]
            vbo = context.buffer(vertex_texcoord.view(np.ubyte))
            self.set_vao(context, shader, vbo)

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.texture.use()
            self.shader['alpha'].value = self.alpha
            self.vao.render(mgl.TRIANGLE_STRIP)

    @classmethod
    def set_vao(cls, context, shader, vbo):
        # re-use VAO
        cls.vao = context.simple_vertex_array(shader, vbo, 'vertices', 'texcoord')
