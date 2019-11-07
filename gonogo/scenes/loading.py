from pkg_resources import resource_filename
from gonogo.visuals.intro_dlg import IntroDlg
from mglg.graphics.shaders import FlatShader, TextShader
from mglg.graphics.text2d import Text2D, FontManager
from mglg.graphics.shape2d import Square
from gonogo.visuals.loading import LoadingCircs
from gonogo.visuals.online_plot import OnlinePlot
from toon.anim import Track, Player
from toon.anim.easing import linear
from toon.anim.interpolators import select
import imgui
from gonogo.visuals.imgui_abstractions import ProgrammablePygletRenderer

# TODO: detect device, show photosensor position beforehand


class Loading(object):
    def __init__(self, win, recipe_dir=None, can_rush=False):
        self._imrender = ProgrammablePygletRenderer(win._win)
        ubuntu_font = resource_filename('gonogo', 'resources/fonts/UbuntuMono-R.ttf')
        self.intro_dlg = IntroDlg(self._imrender, (win.width, win.height), 
                                  recipe_dir=recipe_dir, font=ubuntu_font)
        flat = FlatShader(win.context)
        self.loading = LoadingCircs(win.context, flat)
        self.win = win
        self.can_rush = can_rush

        text_shader = TextShader(win.context)

        font = FontManager.get(ubuntu_font, size=64)

        self.no_rush = Text2D(win.context, text_shader, win.width,
                              win.height, 'Run as administrator for better performance.',
                              font, scale=0.03, position=(0, -0.45),
                              color=(0.9, 0.2, 0.2, 1))
        self.no_device = Text2D(win.context, text_shader, win.width,
                                win.height, 'Device not plugged in. Please plug in and restart.',
                                font, scale=0.03, position=(0, -0.35),
                                color=(0.9, 0.2, 0.2, 1))

        # exit anim
        dlg_fade = Track([(0, 1.0), (1, 0.0)])
        load_fade = Track([(0, 180/255), (1, 0.0)])
        light_screen = Track([(0, 0.3), (1, 0.5)])

        self.photo = Square(win.context, flat, is_outlined=False,
                            fill_color=(1, 1, 1, 1), scale=(0.05, 0.05),
                            position=(0.85, 0))

        self.player = Player()
        self.player.add(dlg_fade, 'alpha', self.intro_dlg)
        self.player.add(load_fade, 'alpha', self.loading)
        self.player.add(light_screen, 'xyz', self.win.background_color)

        self.player_photo = Player(repeats=100000)
        phot_trk = Track([(0, 0), (0.5, 1), (0.5 + win.frame_period * 2, 0)], interpolator=select)
        self.player_photo.add(phot_trk, 'xyz', self.photo.fill_color)

        self.online = OnlinePlot()

    def run(self, device, device_type):
        # loop until response
        done = False
        with device:
            self.player_photo.start(self.win.current_time)
            while not done:
                imgui.new_frame()
                if not self.can_rush:
                    self.no_rush.draw(self.win.cam)
                if device_type != 'custom':
                    self.no_device.draw(self.win.cam)
                else:
                    # draw online thing
                    data = device.read()
                    self.online.update(data)
                self.loading.draw(self.win.cam)
                done, sets = self.intro_dlg.update()
                self.player_photo.advance(self.win.current_time)
                self.photo.draw(self.win.cam)
                imgui.render()
                self._imrender.render(imgui.get_draw_data())
                self.win.flip()
            #
            self.player.start(self.win.current_time)
            while self.player.is_playing:
                imgui.new_frame()
                self.player.advance(self.win.current_time)
                self.player_photo.advance(self.win.current_time)
                self.loading.draw(self.win.cam)
                d, s = self.intro_dlg.update()
                imgui.render()
                self._imrender.render(imgui.get_draw_data())
                self.win.flip()
        return sets


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Win
    win = Win()

    xx = Loading(win, recipe_dir='recipes/')
    res = xx.run()
    print(res)
