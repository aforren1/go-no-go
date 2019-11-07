import numpy as np
#
from gonogo.scenes.base_drop import BaseDrop
from gonogo.visuals.traffic import Traffic
# graphics
from mglg.graphics.shaders import FlatShader
from mglg.graphics.shape2d import Square
# animation
from toon.anim import Player, Track
from toon.anim.interpolators import select
from toon.input import stack


class Practice(BaseDrop):
    # same expected_handler_keys & trial_data_keys as Base

    def __init__(self, win, block_handler, device, user_settings):
        super().__init__(win, block_handler, device, user_settings)

        flat_shader = FlatShader(win.context)

        # hline position is determined by user_settings
        self.hline = Square(win.context, flat_shader, is_outlined=False,
                            fill_color=(0.9, 0.9, 0.9, 1), scale=(2, 0.004))

        self.traffic = Traffic(win, num=self.block_handler.trial_by_trial_settings['t_max'].consecutive)

        self.flats.insert(0, self.hline)
        self.flats.insert(0, self.traffic)

    def run_trial(self):
        # do a little here if the timing has changed
        data_stack, dropped_frames = super().run_trial()
        is_custom_device = self.user_settings['device_type'] == 'custom'
        current_settings = self.block_handler.previous_trials[-1]
        t_delay = current_settings['t_pretrial'] + current_settings['t_windup']
        trial_player = self.trial_player
        t_start = trial_player.ref_time
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
            if good_timing:
                self.ball.visible = False
                self.particle_burst.visible = True
                self.particle_burst.position = self.ball.position.copy()
                self.check.visible = True
                self.traffic.next()
            else:
                self.shadow.visible = True
                self.shadow.position = self.ball.position.copy()
                self.x.visible = True
                self.traffic.reset()

        else:
            press_choice = -1
            press_time = -1
            good_timing = False
            self.x.visible = True
            self.traffic.reset()

        if good_timing:
            self.good_sound.play()
        else:
            self.bad_sound.play()

        feedback_data = self.feedback_loop()
        long_data = stack([data_stack, feedback_data])
        summary_data = current_settings.copy()
        summary_data['choice'] = press_choice
        summary_data['t_choice'] = press_time
        summary_data['correct_choice'] = int(good_timing)
        summary_data['good_timing'] = int(good_timing)
        summary_data['id'] = self.user_settings['id']
        summary_data['datetime'] = self.datetime
        summary_data['block'] = self.block_handler.text_dict['block_key']
        self.write_data(summary_data, long_data, t_start + t_delay, dropped_frames)
        # update to cue finish
        self.block_handler.update_user_data(summary_data)

    def setup_trial(self):
        next_settings = super().setup_trial()
        self.ball.fill_color.rgb = next_settings['ball_color']

        y_line = next_settings['y_line']
        self.hline.position.y = y_line
        self.traffic.scale = 0.2
        self.traffic.position = 0.4, y_line + self.traffic.scale.y/4 + 0.002
        self.traffic.reset_pos()

        # if the t_max has changed, indicate
        # do we want a traffic light thing? can put in the corner somewhere
