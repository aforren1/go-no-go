import os
import glob
from gonogo.visuals.imgui_abstractions import ProgrammablePygletRenderer

import imgui
from imgui import WINDOW_NO_RESIZE, WINDOW_NO_MOVE, WINDOW_NO_COLLAPSE


class IntroDlg(object):
    def __init__(self, renderer, win_dims, recipe_dir, font=None, font_size=30):
        self.center_x = win_dims[0] // 2
        self.center_y = win_dims[1] // 2
        fnt = renderer.io.fonts
        self.extra_font = None
        self.flags = WINDOW_NO_RESIZE | WINDOW_NO_MOVE | WINDOW_NO_COLLAPSE
        if font:
            self.extra_font = fnt.add_font_from_file_ttf(
                font, font_size, fnt.get_glyph_ranges_latin())
        renderer.refresh_font_texture()
        # user settings
        self.id = ''
        self.current_recipe = 0
        self.alpha = 1
        # fixed for now (find defaults in recipes/defaults/)
        self.recipe_dir = recipe_dir
        self.spanish = False

    def update(self):
        # return done, value
        do_return = False
        recipe = ''
        if self.extra_font:
            imgui.push_font(self.extra_font)
        width = 750
        height = 250
        imgui.set_next_window_size(width, height)
        imgui.set_next_window_position(
            self.center_x - width//2, self.center_y - height//2)
        imgui.push_style_var(imgui.STYLE_ALPHA, self.alpha)
        imgui.begin('Drop', False, flags=self.flags)
        self.left_label('ID:')
        xx, self.id = imgui.input_text('\n', self.id, 128)
        self.tooltip_help('Participant ID/Name')

        self.add_space(3)
        self.left_label('Español:')
        _, self.spanish = imgui.checkbox('', self.spanish)
        self.tooltip_help('Spanish text for subsequent instructions')
        self.add_space(3)

        self.left_label('Recipe:')
        # current filenames
        recipe_names = []
        recipe_short = []
        for file in glob.glob('recipes/**/*.toml', recursive=True):
            if (os.path.sep + 'defaults' + os.path.sep) not in file:
                recipe_names.append(file)
                recipe_short.append(os.path.relpath(file, 'recipes'))
        changed, self.current_recipe = imgui.combo(' ', self.current_recipe,
                                                   recipe_short)
        self.tooltip_help(
            'Available recipes (TOML files) in the recipe directory')
        imgui.same_line()
        imgui.button('Preview')
        if imgui.is_item_hovered() and recipe_names:
            with open(recipe_names[self.current_recipe], 'r') as f:
                prev = f.read()
            # width in characters, height in number of newlines
            if prev:
                wid = len(
                    max(open(recipe_names[self.current_recipe], 'r'), key=len))
                # TODO: need to be careful of newline char??
                hei = prev.count('\n') + 1
            else:
                wid = 10
                hei = 1
            fac = 0.6
            font_size = imgui.get_font_size() * fac
            wid = int(wid * font_size / 2)  # get something like pix
            hei = int(hei * font_size)
            # if height is >= half the window height, turn to scroll
            val = hei
            if hei >= self.center_y:
                val = self.center_y
            imgui.begin_tooltip()
            imgui.begin_child('region', wid, val)
            imgui.set_scroll_y(imgui.get_scroll_y() -
                               imgui.get_io().mouse_wheel * 30)
            imgui.set_window_font_scale(fac)
            imgui.text(prev)
            imgui.end_child()
            imgui.end_tooltip()
            imgui.set_item_default_focus()

            # imgui.set_tooltip(prev)
        self.add_space(3)

        if imgui.button('Ok'):
            do_return = True
        if imgui.get_io().keys_down[imgui.KEY_ENTER]:
            do_return = True

        imgui.pop_style_var(1)
        imgui.end()
        if self.extra_font:
            imgui.pop_font()

        # disallow depending on current state
        if not self.id:
            do_return = False
        try:
            recipe = recipe_names[self.current_recipe]
        except IndexError:
            do_return = False
        if not os.path.isdir(self.recipe_dir):
            do_return = False
        # no need to validate data dir, we'll create it
        data = {'id': self.id, 'recipe': recipe,
                'spanish': 'es' if self.spanish else 'en'}
        return do_return, data

    def tooltip_help(self, txt):
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text(txt)
            imgui.end_tooltip()

    def add_space(self, spaces):
        for i in range(spaces):
            imgui.spacing()

    def left_label(self, txt):
        imgui.text(txt)
        imgui.same_line()


if __name__ == '__main__':
    from pkg_resources import resource_filename

    import moderngl as mgl
    from gonogo.visuals.window import ExpWindow as Win
    from mglg.graphics.shaders import FlatShader
    from mglg.graphics.shape2d import Circle
    from mglg.graphics.camera import Camera
    from gonogo.visuals.projection import height_ortho

    win = Win()
    ortho = height_ortho(win.width, win.height)
    cam = Camera(projection=ortho)
    flt = FlatShader(win.context)
    cir = Circle(win.context, flt, scale=(0.5, 0.5), is_filled=False)
    xx = IntroDlg(win._win, recipe_dir='', font=resource_filename(
        'gonogo', 'resources/fonts/UbuntuMono-R.ttf'))

    dr = False

    while not dr:
        cir.draw(cam)
        dr, txt = xx.update()
        #xx.alpha -= win.dt/10
        xx.draw()
        win.flip()
    print(txt)
