from timeit import default_timer

from pkg_resources import resource_filename

from mglg.graphics.drawable import DrawableGroup
from mglg.graphics.shaders import TextShader
from mglg.graphics.text2d import FontManager, Text2D
from toon.anim import Player, Track
from toon.anim.interpolators import select
from toon.anim.easing import exponential_out


class Countdown(object):
    def __init__(self, win):
        text_shader = TextShader(win.context)
        text_path = resource_filename('gonogo', 'resources/fonts/Baloo-Regular.ttf')
        font = FontManager.get(text_path, size=128)
        self.cam = win.cam

        self.texts = []
        nums = ['3', '2', '1', '!']
        cols = [(0.111, 1, 0.133, 1), (1, 1, .133, 1),
                (1, .678, .133, 1), (1, .294, .133, 1)]
        for num, col in zip(nums, cols):
            self.texts.append(Text2D(win.context, text_shader, win.width, win.height,
                                     num, font, position=(0, 0), color=col, visible=False))
        self.dg = DrawableGroup(self.texts)
        # one track per text
        period = 0.5
        offsets = [0.1, 0.6, 1.2, 1.8]
        self.player = Player()
        for i in range(len(offsets)):
            # .visible
            vis_track = Track([(0, 0), (offsets[i], 1),
                               (offsets[i] + period, 0)], interpolator=select)
            # .scale
            scale_track = Track([(0, 0.1), (offsets[i], 0.3),
                                 (offsets[i] + period, 0.1)], easing=exponential_out)
            self.player.add(vis_track, 'visible', self.texts[i])
            self.player.add(scale_track, 'scale', self.texts[i])

    def start(self):
        self.player.start(default_timer())

    def draw(self):
        self.player.advance(default_timer())
        self.dg.draw(self.cam)


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Win

    win = Win()
    countd = Countdown(win)

    countd.start()
    while countd.player.is_playing:
        countd.draw()
        win.flip()
