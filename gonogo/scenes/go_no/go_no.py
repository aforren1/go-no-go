import numpy as np

from gonogo.scenes.base_drop import BaseDrop
from mglg.graphics.shaders import FlatShader
from mglg.graphics.shape2d import Square
# animation
from toon.anim import Player, Track
from toon.anim.interpolators import select
from toon.input import stack


class GoNo(BaseDrop):
    expected_handler_keys = ['initial', 'final', 'no_go_colors'] + BaseDrop.expected_handler_keys
    trial_data_keys = BaseDrop.trial_data_keys

    def __init__(self, win, block_handler, device, user_settings):
        super().__init__(win, block_handler, device, user_settings)

        flat_shader = FlatShader(win.context)

        # hline position is determined by user_settings
        self.hline = Square(win.context, flat_shader, is_outlined=False,
                            fill_color=(0.9, 0.9, 0.9, 1), scale=(2, 0.004))

        self.flats.insert(0, self.hline)

    def run_trial(self):
        data_stack, dropped_frames = super().run_trial()
        is_custom_device = self.user_settings['device_type'] == 'custom'
        current_settings = self.block_handler.previous_trials[-1]
        t_delay = current_settings['t_pretrial'] + current_settings['t_windup']
        trial_player = self.trial_player
        t_start = trial_player.ref_time
        final_state = current_settings['final']
        final_color = current_settings['no_go_colors'][final_state]

        is_go = bool(final_state)
        if data_stack.any():
            if is_custom_device:
                any_pressed = (data_stack.buttons > 0).any()
            else:
                any_pressed = any(data_stack.press)
        if data_stack.any() and any_pressed:
            if is_custom_device:
                index_max_per_button = np.argmax(data_stack.buttons, axis=0)
                # we want the smallest non-zero value
                best_choice = None
                best_index = None
                for count, value in enumerate(index_max_per_button):
                    if value > 0:
                        if best_choice is None:
                            best_choice = count
                            best_index = value
                        # lower non-zero index than current best
                        elif value <= best_index:
                            best_choice = count
                            best_index = value

                # press time relative to the start of movement
                press_time = data_stack.buttons.time[best_index] - t_start - t_delay
                press_choice = best_choice
            else:
                index = np.argmax(data_stack.press)
                press_time = data_stack.press.time[index] - t_start - t_delay
                press_choice = data_stack.index[index]
            lb = current_settings['t_max'] - current_settings['timing_tol']
            ub = current_settings['t_max'] + current_settings['timing_tol']
            good_timing = press_time >= lb and press_time <= ub
            trial_player.advance(t_start + press_time + t_delay)
            if good_timing and is_go:
                self.ball.visible = False
                self.particle_burst.visible = True
                self.particle_burst.position = self.ball.position.copy()
                self.check.visible = True
                correct_choice = True
            elif good_timing:  # pressed on a no-go, but good timing
                self.ball.visible = False
                self.ball2.visible = True
                self.ball2.position = self.ball.position.copy()
                self.ball2.fill_color.xyz = final_color
                self.x.visible = True
                correct_choice = False
            else:  # pressed on a no-go, not good timing
                self.shadow.visible = True
                self.shadow.position = self.ball.position.copy()
                self.x.visible = True
                correct_choice = False
        else:  # no response
            good_timing = True  # well, not quite true?
            press_time = -1
            press_choice = -1
            if not is_go:
                correct_choice = True
                self.check.visible = True
            else:
                correct_choice = False
                self.x.visible = True

        if correct_choice and good_timing:
            self.good_sound.play()
        else:
            self.bad_sound.play()
        feedback_data = self.feedback_loop()
        long_data = stack([data_stack, feedback_data])
        # TODO: subtract off t_start from the long_data timestamp?
        summary_data = current_settings.copy()
        summary_data['choice'] = press_choice
        summary_data['t_choice'] = press_time
        summary_data['correct_choice'] = int(correct_choice)
        summary_data['good_timing'] = int(good_timing)
        summary_data['id'] = self.user_settings['id']
        summary_data['datetime'] = self.datetime
        self.write_data(summary_data, long_data, t_start + t_delay, dropped_frames)

    def setup_trial(self):
        next_settings = super().setup_trial()

        y_line = next_settings['y_line']
        t_max = next_settings['t_max']
        t_pretrial = next_settings['t_pretrial']
        t_windup = next_settings['t_windup']
        t_waiting = t_pretrial + t_windup

        self.hline.position.y = y_line

        # the key thing-- ball jump direction (block specific)
        # make sure to use 'select' as the interpolator
        t_prep = next_settings['t_prep']
        initial_state = next_settings['initial']
        final_state = next_settings['final']
        initial_color = next_settings['no_go_colors'][initial_state]
        final_color = next_settings['no_go_colors'][final_state]
        ball_color = [(0, initial_color), (t_waiting, initial_color),
                      (t_waiting + (t_max - t_prep), final_color)]
        ball_color = Track(ball_color, interpolator=select)
        self.trial_player.add(ball_color, 'rgb', self.ball.fill_color)


if __name__ == '__main__':
    from gonogo.visuals.window import ExpWindow as Window
    from gonogo.settings.resolve import resolve_settings
    from gonogo.settings.block_handler import BlockHandler
    from gonogo.utils import camel_to_snake, snake_to_camel
    from inspect import isclass
    from gonogo.scenes import GoNoInstr
    from toon.input import MpDevice as MpD
    from gonogo.devices.keyboard import Keyboard
    from gonogo.scenes.block import Block
    from time import sleep

    win = Window()
    default_recipes = 'recipes/defaults/'
    bh_material, resolved_dict = resolve_settings('recipes/test_gono.toml',
                                                  default_recipes)

    block_handlers = [BlockHandler(x, y) for x, y in zip(bh_material, resolved_dict)]

    block_dict = {}
    # find experiments that have been imported
    lc = locals()
    existing_exps = {k: lc[k] for k in lc.keys() if isclass(lc[k]) and issubclass(lc[k], Block)}
    del existing_exps['Block']  # remove the base class

    blocks = []
    device = MpD(Keyboard(keys=['k', 'l'], clock=win.clock))
    user_settings = {'id': '007', 'data_dir': '/dev/null'}
    for bh in block_handlers:
        # extract the class
        stc = snake_to_camel(bh.name)
        exp_cls = existing_exps[stc]
        prac_cls = lc[stc + 'Instr']
        # instantiate the classes (one for instructions, one for block)
        blocks.append(prac_cls(win, device))
        blocks.append(exp_cls(win, bh, device, user_settings))

    blocks[1].run()
