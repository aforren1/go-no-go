from timeit import default_timer

from pkg_resources import resource_filename

from mglg.graphics.shaders import FlatShader, TextShader
from mglg.graphics.shape2d import Square
from mglg.graphics.text2d import Text2D, FontManager

# Pictoral representation of button box
# fixed size for simplicity
# this begs a scenegraph (for relative positioning)


class MockButtons(object):

    def __init__(self, win, keys=['K', 'L']):
        flat_shader = FlatShader(win.context)
        text_shader = TextShader(win.context)
        # base
        self.subbase = Square(win.context, flat_shader, fill_color=(1, 1, 1, 1),
                              is_outlined=False, position=(0.54, -0.26),
                              scale=(0.42, 0.22))
        self.base = Square(win.context, flat_shader, fill_color=(0.1, 0.1, 0.3, 1),
                           outline_color=(1, 1, 1, 1), position=(0.54, -0.26),
                           scale=(0.4, 0.2))

        # keys
        self.left_key = Square(win.context, flat_shader, fill_color=(0.4, 0.4, 0.4, 1),
                               outline_color=(1, 1, 1, 1), position=(0.44, -0.26),
                               scale=(0.15, 0.15), is_outlined=False)
        self.right_key = Square(win.context, flat_shader, fill_color=(0.4, 0.4, 0.4, 1),
                                outline_color=(1, 1, 1, 1), position=(0.64, -0.26),
                                scale=(0.15, 0.15), is_outlined=False)

        text_path = resource_filename('gonogo', 'resources/fonts/FreeSans.ttf')
        font = FontManager.get(text_path, size=128)

        self.left_txt = Text2D(win.context, text_shader, win.width,
                               win.height, keys[0], font,
                               scale=(0.06, 0.06), position=(0.44, -0.26))
        self.right_txt = Text2D(win.context, text_shader, win.width,
                                win.height, keys[1], font,
                                scale=(0.06, 0.06), position=(0.64, -0.26))

    def draw(self, cam):
        self.subbase.draw(cam)
        self.base.draw(cam)
        self.left_key.draw(cam)
        self.right_key.draw(cam)
        self.left_txt.draw(cam)
        self.right_txt.draw(cam)


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Win

    win = Win(background_color=(0.7, 0.6, 0.5, 1))
    xx = MockButtons(win, keys=['L', '\u2192'])

    while True:
        xx.draw(win.cam)
        win.flip()
