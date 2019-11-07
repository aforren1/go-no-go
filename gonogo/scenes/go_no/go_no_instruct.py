from timeit import default_timer
from math import inf
from toon.anim import Track, Player
from toon.anim.interpolators import select
from toon.anim.easing import smootherstep
from mglg.graphics.shape2d import Circle, Square
from mglg.graphics.drawable import DrawableGroup
from mglg.graphics.shaders import FlatShader
from gonogo.scenes.base_instruction import BaseInstruction


class GoNoInstr(BaseInstruction):
    title = 'Go/No'

    instruction_text = {'en': 'Press the left key when the %s circle intersects the line. Do not press the key when the circle is %s.',
                        'es': 'Pulse la tecla izquierda cuando el círculo %s cruza la línea. No pulse la tecla cuando el círculo es %s.'}

    def __init__(self, win, block_handler, device, settings, number=1, total=10):
        white = {'en': 'white', 'es': 'blanco'}
        black = {'en': 'black', 'es': 'negro'}
        go_color = block_handler.text_dict['no_go_colors'][1]
        no_color = block_handler.text_dict['no_go_colors'][0]
        if go_color == 1:
            col1 = white
            col2 = black
        else:
            col1 = black
            col2 = white
        self.is2 = self.instruction_text.copy()
        self.instruction_text['en'] = self.instruction_text['en'] % (col1['en'], col2['en'])
        self.instruction_text['es'] = self.instruction_text['es'] % (col1['es'], col2['es'])
        super().__init__(win, device, settings, number, total)
        self.instruction_text['en'] = self.is2['en']
        self.instruction_text['es'] = self.is2['es']
        # visuals

        flat_shader = FlatShader(win.context)
        # scales & things are approximate, the exact ones are calculated
        # trial-by-trial and depend on various settings (timing tolerance,
        # initial position, ...)
        self.ball = Circle(win.context, flat_shader, fill_color=(1, 1, 1, 1),
                           scale=(0.1, 0.1), position=(0, 0))
        self.hline = Circle(win.context, flat_shader, is_outlined=False,
                            fill_color=(0.4, 0.4, 0.4, 1), scale=(2, 0.005),
                            position=(0, -0.3))
        # DrawableGroups clean up the main loop & can be used to
        # cluster drawables together that use the same shader (which
        # improves perf)
        self.dg = DrawableGroup([self.hline, self.ball])

        # animations
        self.player = Player(repeats=inf)

        # ball trajectory (y)
        ball_traj_y = [(0, 0.4), (0.3, 0.4), (1, -0.3), (1.3, -0.3), (1.301, 0.4),
                       (1.6, 0.4), (1.9, 0.4), (2.6, -0.3), (2.9, -0.6), (2.901, 0.4)]
        ball_traj_y = Track(ball_traj_y)
        self.player.add(ball_traj_y, 'y', self.ball.position)

        # ball color
        ball_traj_x = [(0, go_color), (0.65, go_color),
                       (1.301, no_color), (2.25, no_color)]
        ball_traj_x = Track(ball_traj_x, interpolator=select)
        self.player.add(ball_traj_x, 'rgb', self.ball.fill_color)

        # ball squish
        # TODO: why doesn't y behave well for scaling?
        orig_y = float(self.ball.scale.y)
        ball_windup = [(0, orig_y), (0.15, orig_y/3), (0.3, orig_y), (1.6, orig_y), (1.75, orig_y/3), (1.9, orig_y)]
        ball_windup = Track(ball_windup)
        self.player.add(ball_windup, 'y', self.ball.scale)

        # key animation
        original_gray = self.mock_keys.left_key.fill_color.g
        key_green = [(0, original_gray), (0.9, original_gray), (1, 0.9),
                     (1.2, original_gray), (1.6, original_gray),
                     (2.5, original_gray), (2.6, original_gray),
                     (2.8, original_gray)]

        left_green = Track(key_green, easing=smootherstep)
        self.player.add(left_green, 'g', self.mock_keys.left_key.fill_color)
        self.player.start(default_timer())

    def preview_draw(self, cam):
        # draw the task-specific anim here
        self.player.advance(default_timer())
        self.dg.draw(cam)
