from mglg.graphics.shape2d import Circle
from math import sin, cos


class LoadingCircs(object):
    def __init__(self, context, shader):
        self.t = 0
        self.blue_cir = Circle(context, shader, fill_color=(9/255, 44/255, 92/255, 180/255),
                               is_outlined=False)
        self.blue_cir.scale.xy = 0.08
        self.blue_cir.rotation = 180
        self.blue_cir.position.y = 0.3

        self.white_cir = Circle(context, shader, fill_color=(1, 1, 1, 180/255),
                                is_outlined=False)
        self.white_cir.scale.xy = 0.08
        self.white_cir.position.y = 0.3
        self.alpha = 180/255

    def draw(self, camera):
        self.t += 1/60
        self.blue_cir.scale.x = sin(self.t * .65)/12
        self.blue_cir.scale.y = cos(self.t * .4)/12
        self.white_cir.scale.x = cos(self.t * 1.1)/11
        self.white_cir.scale.y = sin(self.t * 0.55)/13
        self.blue_cir.rotation -= 0.8
        self.white_cir.rotation += 0.5
        self.white_cir.draw(camera)
        self.blue_cir.draw(camera)

    @property
    def alpha(self):
        return self.white_cir.fill_color.w

    @alpha.setter
    def alpha(self, val):
        self.white_cir.fill_color.w = val
        self.blue_cir.fill_color.w = val


if __name__ == '__main__':
    from mglg.graphics.shaders import FlatShader
    from gonogo.visuals.window import ExpWindow as Win

    win = Win()
    flat = FlatShader(win.context)

    lds = LoadingCircs(win.context, flat)

    while True:
        lds.draw(win.cam)
        win.flip()
