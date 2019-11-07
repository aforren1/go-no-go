from abc import ABCMeta, abstractmethod
from math import cos, sin
from timeit import default_timer

import imgui
from imgui import WINDOW_NO_COLLAPSE, WINDOW_NO_MOVE, WINDOW_NO_RESIZE, WINDOW_NO_TITLE_BAR
from pkg_resources import resource_filename

from gonogo.visuals.imgui_abstractions import ProgrammablePygletRenderer
from gonogo.visuals.render_surface import RenderSurface2D
from mglg.graphics.shaders import FlatShader, ImageShader, TextShader
from mglg.graphics.shape2d import Square
from mglg.graphics.text2d import FontManager, Text2D
from gonogo.visuals.mock_buttons import MockButtons


class BaseInstruction(metaclass=ABCMeta):

    @property
    @abstractmethod
    def title(self):
        # just some brief string, e.g. "Left/Right"
        pass

    @property
    @abstractmethod
    def instruction_text(self):
        # for supported langs:
        # {'en': 'Hello', 'es': 'Hola'}
        pass

    def __init__(self, win, device, settings, number=1, total=10):
        self.win = win
        self.device = device
        default_lang = settings['spanish']
        self.default_lang = default_lang
        self.it2 = self.instruction_text[default_lang]

        flat = FlatShader(self.win.context)
        self.fade_sqr = Square(win.context, flat, is_outlined=False,
                               fill_color=win._background_color, scale=(2, 2))
        self.fade_sqr.fill_color.a = 1

        image_shader = ImageShader(win.context)
        self.preview_surface = RenderSurface2D(win.context, image_shader,
                                               scale=(1, 3/5), position=(1/4, 1/6-0.03),
                                               clear_color=(0.3, 0.3, 0.3, 1))
        text_shader = TextShader(win.context)

        title_path = resource_filename('gonogo', 'resources/fonts/Baloo-Regular.ttf')
        title_font = FontManager.get(title_path, size=64)

        instr_path = resource_filename('gonogo', 'resources/fonts/UbuntuMono-R.ttf')
        instr_font = FontManager.get(instr_path, size=64)

        self.render_title = Text2D(win.context, text_shader, win.width,
                                   win.height, self.title, title_font,
                                   scale=(0.05, 0.05), position=(-0.45, 1/6-0.03))
        if type(device.device).__name__ == 'Keyboard':
            keys = [x.upper() for x in device.device.keys]
        elif type(device.device).__name__ == 'Custom':
            keys = ['\u2190', '\u2192']
        self.mock_keys = MockButtons(win, keys=keys)
        start_txt = {'en': 'Press either key to start.',
                     'es': 'Pulse cualquiera las dos teclas para comenzar.'}

        self.render_start = Text2D(win.context, text_shader, win.width,
                                   win.height, start_txt[default_lang],
                                   instr_font,
                                   color=(0.1, 0.9, 0.2, 0.8), scale=(0.05, 0.05),
                                   position=(0, 0.1))
        self.start_text_bg = Square(win.context, flat, is_outlined=False,
                                    fill_color=(0.1, 0.1, 0.1, 0.8),
                                    scale=(2, 0.06), position=(0, 0.1))

        # imgui stuff
        self.imgui_renderer = ProgrammablePygletRenderer(win._win)
        fnt = self.imgui_renderer.io.fonts
        self.imgui_font = fnt.add_font_from_file_ttf(instr_path, 26, fnt.get_glyph_ranges_latin())
        self.imgui_renderer.refresh_font_texture()
        self.flags = WINDOW_NO_RESIZE | WINDOW_NO_MOVE | WINDOW_NO_COLLAPSE
        self.imgui_dims = int(4/3*win.height), int(1/4 * win.height)
        self.imgui_pos = win.width//7, int((win.height/2) + self.imgui_dims[1] * 4/5)
        self.t0 = default_timer()
        self.can_finish = False
        self.fade_in = True
        self.fade_out = False
        self.num = number
        self.tot = total

    def draw(self, data):
        # render to texture
        time = default_timer() - self.t0
        with self.preview_surface:
            self.preview_draw(self.preview_surface.cam)
            # start flashing message & allow input
            if time > 3.14:
                self.can_finish = True
                self.render_start.color.a = sin(time*3)/2 + 0.85
                self.start_text_bg.draw(self.preview_surface.cam)
                self.render_start.draw(self.preview_surface.cam)
            self.mock_keys.draw(self.preview_surface.cam)
        self.preview_surface.draw(self.win.cam)
        self.render_title.draw(self.win.cam)

        # imgui window
        imgui.new_frame()
        imgui.push_font(self.imgui_font)
        imgui.set_next_window_size(*self.imgui_dims)
        imgui.set_next_window_position(*self.imgui_pos)
        title = {'en': 'Instructions', 'es': 'Instrucciones'}
        imgui.begin(title[self.default_lang], False, flags=self.flags)
        imgui.push_text_wrap_pos(1000)
        imgui.text(self.it2)
        imgui.pop_text_wrap_pos()
        imgui.end()
        imgui.set_next_window_position(100, 100)
        imgui.set_next_window_size(180, 50)
        imgui.begin('##blockcount', flags=self.flags | WINDOW_NO_TITLE_BAR)
        rnd = {'en': 'Round', 'es': 'La ronda'}
        imgui.text('%s %s/%s' % (rnd[self.default_lang], self.num, self.tot))
        imgui.end()
        imgui.pop_font()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())
        # fade in effect
        if self.fade_in:
            self.fade_sqr.fill_color.a -= 0.05
            if self.fade_sqr.fill_color.a <= 0:
                self.fade_in = False
            self.fade_sqr.draw(self.win.cam)
        if self.fade_out:
            self.fade_sqr.fill_color.a += 0.05
            self.fade_sqr.draw(self.win.cam)
            if self.fade_sqr.fill_color.a >= 1:
                return True
        if data and self.can_finish:
            self.fade_out = True
        return False

    def preview_draw(self, cam):
        pass

    def run(self):
        self.t0 = default_timer()
        done = False
        kbd = self.device
        win = self.win
        any_pressed = False
        with kbd as dev:
            while not done:
                data = dev.read()
                if data.any():
                    if type(dev.device).__name__ == 'Custom':
                        any_pressed = (data.buttons > 0).any()
                    else:
                        any_pressed = any(data.press)
                else:
                    data = None
                done = self.draw(any_pressed)
                win.flip()


class Test(BaseInstruction):
    title = 'FooBar'
    instruction_text = {'en': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                        'es': 'Lorem ipsum dolor sit amet, elit adipiscing del consectetur, tempor sed y vitalidad, por lo que el trabajo y dolor, algunas cosas importantes que hacer eiusmod. Con los años, entraré, que nostrud aliquip fuera de ella la ventaja de ejercicio, por lo que los esfuerzos de estímulo si el distrito escolar y la longevidad.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        flat = FlatShader(self.win.context)
        self.sqr = Square(self.win.context, flat, scale=(0.1, 0.1),
                          rotation=30)

    def preview_draw(self, cam):
        self.sqr.rotation += 4
        self.sqr.draw(cam)


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Win
    from toon.input import MpDevice as MpD
    from gonogo.devices.keyboard import Keyboard
    win = Win(background_color=(0.5, 0.5, 0.5, 1))
    kbd = MpD(Keyboard(keys=['k', 'l']))

    xx = Test(win, kbd, 'en')
    done = False
    with kbd as dev:
        while not done:
            data = dev.read()
            if data.any():
                if type(dev.device).__name__ == 'Custom':
                    any_pressed = (data.buttons > 0).any()
                else:
                    any_pressed = any(data.press)
            else:
                data = None
            done = xx.draw(data)
            win.flip()
