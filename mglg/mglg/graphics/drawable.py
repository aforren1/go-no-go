import abc
import numpy as np
from mglg.graphics.object import Object2D
from mglg.graphics.camera import Camera
from moderngl import Context, Program


class Drawable(abc.ABC):
    def __init__(self, context: Context, shader: Program, visible=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = visible
        self.shader = shader
        self.mvp = np.eye(4, dtype=np.float32)
        self._mvp_ubyte_view = self.mvp.view(np.ubyte)  # use this one for sending to moderngl

    @abc.abstractmethod
    def draw(self, camera: Camera):
        pass
        # if self.visible:
        #     # it seems like @ is ~1.5x slower than dot for this sort of problem,
        #     # though the absolute difference is 1.83 us vs 1.18 us
        #     np.dot(self.model_matrix, camera.vp, self.mvp)
        #     self.shader['mvp'].write(self._mvp_ubyte_view)
        #     self.vao.render() and the like


class Drawable2D(Drawable, Object2D):
    pass


class DrawableGroup(list):
    # at this point, it's just a dumb list of things using the
    # same shader-- for glumpy, it made a little more sense 'cause
    # the program was explicitly bound/unbound
    # moderngl maintains which program was bound last, so this does
    # provide the same effective benefit -- not calling a bunch of `glUseProgram`s

    # the other benefit is toggling visibility for a large number of Drawables
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = True

    def draw(self, camera: Camera):
        if self.visible:
            for obj in self:
                obj.draw(camera)
