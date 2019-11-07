from timeit import default_timer
from math import inf
from toon.anim import Track, Player
from toon.anim.interpolators import select
from toon.anim.easing import smootherstep
from mglg.graphics.shape2d import Circle, Square
from mglg.graphics.drawable import DrawableGroup
from mglg.graphics.shaders import FlatShader
from gonogo.scenes.base_instruction import BaseInstruction


class PracticeInstr(BaseInstruction):
    title = 'Practice'

    instruction_text = {'en': 'Practice pressing the left button when the circle intersects with the line.',
                        'es': 'Practique pulsar la tecla izquierda cuando el círculo blanco cruza la línea.'}

    def __init__(self, win, block_handler, device, settings, number=1, total=10):
        super().__init__(win, device, settings, number, total)

        # visuals
        flat_shader = FlatShader(win.context)
        # scales & things are approximate, the exact ones are calculated
        # trial-by-trial and depend on various settings (timing tolerance,
        # initial position, ...)
        ball_color = block_handler.text_dict['ball_color']
        self.ball = Circle(win.context, flat_shader,
                           fill_color=(ball_color, ball_color, ball_color, 1),
                           scale=(0.1, 0.1), position=(0, 0))
        self.hline = Square(win.context, flat_shader, is_outlined=False,
                            fill_color=(0.4, 0.4, 0.4, 1), scale=(2, 0.005),
                            position=(0, -0.3))
        self.dg = DrawableGroup([self.hline, self.ball])

        self.player = Player(repeats=inf)

        ball_traj = Track([(0, 0.4), (0.3, 0.4), (1, -0.3), (1.3, -0.3)])
        self.player.add(ball_traj, 'y', self.ball.position)

        # ball squish
        # TODO: why doesn't y behave well for scaling?
        orig_y = float(self.ball.scale.y)
        ball_windup = [(0, orig_y), (0.15, orig_y/3), (0.3, orig_y)]
        ball_windup = Track(ball_windup)
        self.player.add(ball_windup, 'y', self.ball.scale)

        # key animation
        original_gray = self.mock_keys.left_key.fill_color.g
        key_green = [(0, original_gray), (0.9, original_gray), (1, 0.9),
                     (1.2, original_gray)]

        left_green = Track(key_green, easing=smootherstep)
        self.player.add(left_green, 'g', self.mock_keys.left_key.fill_color)
        self.player.start(default_timer())

    def preview_draw(self, cam):
        self.player.advance(default_timer())
        self.dg.draw(cam)
