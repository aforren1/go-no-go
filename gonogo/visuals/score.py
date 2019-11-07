import imgui
from imgui import (WINDOW_NO_COLLAPSE, WINDOW_NO_MOVE, WINDOW_NO_RESIZE,
                   WINDOW_NO_TITLE_BAR)

from gonogo.visuals.imgui_abstractions import ProgrammablePygletRenderer
from pkg_resources import resource_filename


class ScoreCard(object):
    def __init__(self, win):
        self.renderer = ProgrammablePygletRenderer(win)
        self.center_x = win.width//2
        self.center_y = win.height//2
        self.visible = False

        self.flags = WINDOW_NO_COLLAPSE | WINDOW_NO_MOVE | WINDOW_NO_RESIZE | WINDOW_NO_TITLE_BAR
        fnt = self.renderer.io.fonts

        font_name = resource_filename('gonogo', '/resources/fonts/UbuntuMono-R.ttf')
        self.extra_font = fnt.add_font_from_file_ttf(font_name, 32)
        self.renderer.refresh_font_texture()
        self.col1 = 0.9, 0.2, 0.1
        self.col2 = 0.9, 0.2, 0.1

    def set_new(self, line1='', line2='', good1=True, good2=False):
        self.line1 = line1
        self.line2 = line2
        if not good1:
            self.col1 = 0.9, 0.2, 0.1
        else:
            self.col1 = 0.2, 0.9, 0.3
        if not good2:
            self.col2 = 0.9, 0.2, 0.1
        else:
            self.col2 = 0.2, 0.9, 0.3

    def update(self):
        imgui.new_frame()
        imgui.push_font(self.extra_font)
        ml = max(len(self.line1), len(self.line2))
        w, h = ml * 32 / 1.5, 3.5 * 32
        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(self.center_x - w//2, self.center_y - h//2)
        imgui.begin('x', False, flags=self.flags)
        imgui.push_style_color(imgui.COLOR_TEXT, *self.col1)
        imgui.text(self.line1)
        imgui.pop_style_color(1)
        self.add_space(4)
        imgui.push_style_color(imgui.COLOR_TEXT, *self.col2)
        imgui.text(self.line2)
        imgui.pop_style_color(1)
        imgui.end()
        imgui.pop_font()
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def add_space(self, spaces):
        for i in range(spaces):
            imgui.spacing()


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Win

    win = Win()
    xx = ScoreCard(win._win)
    xx.set_new('foo', 'bar', True, False)
    while True:
        xx.update()
        win.flip()
