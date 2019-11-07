from toon.anim import Track, Player
from timeit import default_timer
from pkg_resources import resource_filename
from mglg.graphics.shaders import ParticleShader, TextShader
from mglg.graphics.text2d import Text2D, FontManager
from mglg.graphics.particle2d import ParticleBurst2D


class Done(object):
    def __init__(self, win):
        text_shader = TextShader(win.context)
        self.win = win
        particle_shader = ParticleShader(win.context)

        self.particle_burst = ParticleBurst2D(win.context, particle_shader,
                                        scale=(0.05, 0.05), position=(0, 0.1),
                                        num_particles=1e4)

        title_path = resource_filename('gonogo', 'resources/fonts/Baloo-Regular.ttf')
        title_font = FontManager.get(title_path, size=64)

        self.render_title = Text2D(win.context, text_shader, win.width,
                                   win.height, 'Done!', title_font,
                                   scale=(0.05, 0.05), position=(0, 0),
                                   color=(0.1, 0.95, 0.2, 1))
        fade_trk = Track([(0, 1), (3, 0)])

        self.player = Player()
        self.player.add(fade_trk, 'a', self.render_title.color)
    
    def run(self):
        # fade in, fade out
        self.particle_burst.reset()
        self.player.start(default_timer())
        
        while self.player.is_playing:
            self.player.advance(default_timer())
            self.particle_burst.draw(self.win.cam)
            self.render_title.draw(self.win.cam)
            self.win.flip()

