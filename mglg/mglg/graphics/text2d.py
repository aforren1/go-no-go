# either

import numpy as np

import moderngl as mgl
from mglg.graphics.camera import Camera
from mglg.math.vector import Vector4f
from mglg.graphics.drawable import Drawable2D
from mglg.graphics.font.font_manager import FontManager


class Text2D(Drawable2D):
    def __init__(self, context: mgl.Context, shader, width, height,
                 text, font, color=(1, 1, 1, 1), anchor_x='center',
                 anchor_y='center', *args, **kwargs):
        super().__init__(context, shader, *args, **kwargs)
        self.color = Vector4f(color)
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        vertices, indices = self.bake(text, font)
        manager = FontManager()
        atlas = manager.atlas_agg
        self.atlas = context.texture(atlas.shape[0:2], 3, atlas.view(np.ubyte))
        vbo = context.buffer(vertices.view(np.ubyte))
        ibo = context.buffer(indices.view(np.ubyte))
        self.vao = context.vertex_array(shader,
                                        [   # TODO: pad? maybe doesn't matter 'cause we're not streaming
                                            (vbo, '2f 2f 1f', 'vertices', 'texcoord', 'offset')
                                        ],
                                        index_buffer=ibo)

        shader['viewport'].value = width, height
        self.atlas.use()

    def draw(self, camera: Camera):
        if self.visible:
            np.dot(self.model_matrix, camera.vp, self.mvp)
            self.atlas.use()
            self.shader['mvp'].write(self._mvp_ubyte_view)
            self.shader['color'].write(self.color._ubyte_view)
            self.vao.render(mgl.TRIANGLES)

    def bake(self, text, font):
        anchor_x = self.anchor_x
        anchor_y = self.anchor_y
        n = len(text) - text.count('\n')
        indices = np.zeros((n, 6), dtype=np.uint32)
        vertices = np.zeros((n, 4), dtype=[('vertices', np.float32, 2),
                                           ('texcoord', np.float32, 2),
                                           ('offset', np.float32)])

        start = 0
        pen = [0, 0]
        prev = None
        lines = []
        text_width, text_height = 0, 0
        # text is in pixels,
        # position is defining little boxes that texture will go into
        # texcoord defines the local texture location (not sure I get the units?)
        # offset is the offset of the texture??

        index = 0
        for charcode in text:
            if charcode == '\n':
                prev = None
                lines.append(((start, index), pen[0]))
                start = index
                text_width = max(text_width, pen[0])
                pen[1] -= font.height
                pen[0] = 0
            else:
                glyph = font[charcode]
                kerning = glyph.get_kerning(prev)
                x0 = pen[0] + glyph.offset[0] + kerning
                offset = x0-int(x0)
                x0 = int(x0)
                y0 = pen[1] + glyph.offset[1]
                x1 = x0 + glyph.shape[0]
                y1 = y0 - glyph.shape[1]
                u0, v0, u1, v1 = glyph.texcoords
                vertices[index]['vertices'] = ((x0, y0), (x0, y1),
                                               (x1, y1), (x1, y0))
                vertices[index]['texcoord'] = ((u0, v0), (u0, v1),
                                               (u1, v1), (u1, v0))
                vertices[index]['offset'] = offset
                indices[index] = index*4
                indices[index] += np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
                pen[0] = pen[0]+glyph.advance[0]/64. + kerning
                pen[1] = pen[1]+glyph.advance[1]/64.
                prev = charcode
                index += 1

        # now we have positions, etc. in pixels
        lines.append(((start, index+1), pen[0]))
        text_height = (len(lines)-1)*font.height
        text_width = max(text_width, pen[0])

        # Adjusting each line
        # center each line on x
        for ((start, end), width) in lines:
            if anchor_x == 'right':
                dx = -width/1.0
            elif anchor_x == 'center':
                dx = -width/2.0
            else:
                dx = 0
            vertices[start:end]['vertices'] += round(dx), 0

        # Adjusting whole label
        # same: adjust so that pixel-coordinate vertices are centered
        if anchor_y == 'top':
            dy = - (font.ascender + font.descender)
        elif anchor_y == 'center':
            dy = (text_height - (font.descender + font.ascender))/2
        elif anchor_y == 'bottom':
            dy = -font.descender + text_height
        else:
            dy = 0
        vertices['vertices'] += 0, round(dy)
        # make sure it's 1D
        vertices = vertices.ravel()
        # normalize to height (so vertices run from [-0.5, 0.5])
        tmp = vertices['vertices'][:, 1]
        vertices['vertices'][...] = ((vertices['vertices'] - np.min(tmp)) / np.ptp(tmp)) - 0.5
        indices = indices.ravel()
        return vertices, indices

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if isinstance(color, Vector4f):
            self._color = color
        else:
            self._color[:] = color
