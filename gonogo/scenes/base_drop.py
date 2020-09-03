from time import sleep
from timeit import default_timer
from datetime import datetime
import numpy as np
#
from pkg_resources import resource_filename

from gonogo.scenes.block import Block
# graphics
from mglg.graphics.drawable import DrawableGroup
from mglg.graphics.image2d import Image2D
from mglg.graphics.particle2d import ParticleBurst2D
from mglg.graphics.shaders import (FlatShader, ImageShader, ParticleShader)
from mglg.graphics.shape2d import Circle, Square
from gonogo.utils import rush
from gonogo.visuals.countdown import Countdown

# sound
from gonogo.sound import Sound

# animation
from toon.anim import Player, Track
from toon.anim.easing import exponential_in, smoothstep
from toon.anim.interpolators import select
from toon.input import stack

# base for all vertically-dropping variations


class BaseDrop(Block):
    expected_handler_keys = ['y_ball', 'y_line', 't_max',
                             't_pretrial', 't_windup', 't_prep',
                             't_feedback', 'timing_tol']

    trial_data_keys = ['choice', 't_choice', 'correct_choice', 'datetime', 'id']

    def __init__(self, win, block_handler, device, user_settings):
        super().__init__(win, block_handler, device, user_settings)
        # shader setup (might already exist, in which case returns that instance)
        flat_shader = FlatShader(win.context)
        image_shader = ImageShader(win.context)
        particle_shader = ParticleShader(win.context)

        self.fade = Square(win.context, flat_shader, is_outlined=False,
                           fill_color=win._background_color, scale=(2, 2))
        self.fade.visible = False

        # scale & position are determined by user settings
        self.ball = Circle(win.context, flat_shader, fill_color=(1, 1, 1, 1))
        self.ball2 = Circle(win.context, flat_shader, fill_color=(1, 1, 1, 1))
        self.ball2.scale = self.ball.scale  # for good timing, bad response
        self.ball2.visible = False
        self.shadow = Circle(win.context, flat_shader, is_filled=False)

        # this magic lets us avoid explicitly setting the various aspects of this
        # trial-by-trial
        self.shadow.position = self.ball.position
        self.shadow.scale = self.ball.scale
        self.shadow.visible = False

        self.flats = DrawableGroup([self.shadow, self.ball, self.ball2])

        # sugar stuff
        # use .visible to determine the visible image
        check_path = resource_filename('gonogo', 'resources/images/check_small.png')
        x_path = resource_filename('gonogo', 'resources/images/x_small.png')
        self.check = Image2D(win.context, image_shader, check_path,
                             scale=(0.2, 0.2), position=(0, 0))
        self.x = Image2D(win.context, image_shader, x_path,
                         scale=(0.2, 0.2), position=(0, 0))
        self.check.visible = False
        self.x.visible = False
        self.images = DrawableGroup([self.check, self.x])

        # position will be determined by ball position
        # just need to remember to reset() right before playing
        self.particle_burst = ParticleBurst2D(win.context, particle_shader,
                                              scale=(0.025, 0.025),
                                              num_particles=1e4)
        self.particle_burst.visible = False
        self.particle_burst.position = self.ball.position
        self.particles = DrawableGroup([self.particle_burst])

        # photosensor (only with custom device)
        self.photo = Square(win.context, flat_shader, is_outlined=False,
                            fill_color=(1, 1, 1, 1), scale=(0.05, 0.05),
                            position=(0.85, 0))
        if not type(device.device).__name__ == 'Custom':
            self.photo.visible = False
        self.flats.append(self.photo)

        self.countdown = Countdown(win)

        coin_path = resource_filename('gonogo', 'resources/sound/coin.wav')
        self.good_sound = Sound.from_file(coin_path)
        buzz_path = resource_filename('gonogo', 'resources/sound/buzz.wav')
        self.bad_sound = Sound.from_file(buzz_path)
        pop_path = resource_filename('gonogo', 'resources/sound/blop.wav')
        self.pop_sound = Sound.from_file(pop_path)

    def setup_trial(self):
        # set up *all* animations, data path, ...

        # get current trial settings & increment
        next_settings = self.block_handler.next()
        self.trial_player = Player()

        # set up ball motion-- unpack relevant values
        y_ball = next_settings['y_ball']
        y_line = next_settings['y_line']
        t_max = next_settings['t_max']
        t_pretrial = next_settings['t_pretrial']
        t_windup = next_settings['t_windup']
        t_prep = next_settings['t_prep']
        timing_tol = next_settings['timing_tol']

        # set up positions of things here
        self.ball.position.xy = (0, y_ball)
        dist = y_ball - y_line
        speed = dist / t_max
        d_min = speed * (t_max - timing_tol)
        d_max = speed * (t_max + timing_tol)
        self.ball.scale.xy = d_max - d_min

        t_waiting = t_pretrial + t_windup
        t_overshoot = timing_tol * 4
        y_overshoot = -(speed * t_overshoot) + y_line

        ball_traj_y = [(0, y_ball), (t_waiting, y_ball),  # sittin around
                       (t_waiting + t_max, y_line),  # intersect w/line
                       (t_waiting + t_max + t_overshoot, y_overshoot)]  # overshoot if no press
        ball_traj_y = Track(ball_traj_y)
        self.trial_player.add(ball_traj_y, 'y', self.ball.position)

        # photosensor
        # on initially until movement start, then 0 until switch time,
        # then 0 when t_max
        fp2 = self.win.frame_period*2
        photo_alpha = [(0, 1), (fp2, 0),
                       (t_waiting, 1), (t_waiting + fp2, 0),
                       (t_waiting + (t_max - t_prep), 1), (t_waiting + (t_max - t_prep) + fp2, 0),
                       (t_waiting + t_max, 1), (t_waiting + t_max + fp2, 0)]
        photo_alpha = Track(photo_alpha, interpolator=select)
        self.trial_player.add(photo_alpha, 'rgb', self.photo.fill_color)

        # windup
        orig_y = float(self.ball.scale.y)
        ball_windup = [(0, orig_y),
                       (t_pretrial, orig_y),
                       (t_pretrial + (t_windup/2), orig_y/3),
                       (t_pretrial + t_windup, orig_y)]
        ball_windup = Track(ball_windup)

        self.trial_player.add(ball_windup, 'y', self.ball.scale)

        # sound
        pop_play = Track([(0, 'stop'), (t_pretrial + t_windup, 'play')])
        self.trial_player.add(pop_play, 'state', self.pop_sound)

        # feedback animation
        self.particle_burst.reset()  # only simulates when .visible is True
        t_feed = next_settings['t_feedback']
        img_alpha = [(0, 0), (t_feed, 1)]
        orig_scale = float(self.check.scale.x)
        img_scal = [(0, orig_scale/10), (t_feed*3/4, orig_scale)]
        img_alpha = Track(img_alpha, easing=smoothstep)
        img_scal = Track(img_scal, easing=smoothstep)
        self.feedback_anim = Player()
        self.feedback_anim.add(img_alpha, 'alpha', [self.check, self.x])
        self.feedback_anim.add(img_scal, 'xy', [self.check.scale, self.x.scale])

        return next_settings  # pass along

    def draw(self):
        # group all draw stuff together
        cam = self.win.cam
        self.flats.draw(cam)
        self.images.draw(cam)
        self.particles.draw(cam)

    def run(self):
        # take datetime to use across this block
        self.datetime = datetime.now().strftime('%y%m%d_%H%M%S')
        with self.device:  # use context manager version
            while not self.block_handler.should_finish():
                self.setup_trial()
                # if first trial, run fade-in + countdown
                if self.block_handler.counter == 1:
                    self.fade_in()
                self.run_trial()
        self.fade_out()

    def run_trial(self):
        rush(True)
        # locality and all that
        win = self.win
        device = self.device
        is_custom_device = type(device.device).__name__ == 'Custom'
        current_settings = self.block_handler.previous_trials[-1]
        frame_period_tol = win.frame_period * 1.25
        trial_player = self.trial_player
        # use device clock
        trial_player.reset()  # kick everything to t=0
        self.draw()
        win.flip()
        trial_player.start(win.current_time)
        t_start = win.current_time
        device.clear()  # clear any pending data
        response = False
        data_list = []
        dropped_frames = []
        while trial_player.is_playing:
            # read data
            #t0 = default_timer()
            data = device.read()
            data_list.append(data.copy())
            if data.any():
                if is_custom_device:
                    response = (data.buttons > 0).any()
                else:
                    response = any(data.press)
                if response:
                    break
            # advance visuals to estimated next frame period
            trial_player.advance(win.current_time + win.frame_period)
            self.draw()
            #t1 = default_timer()
            win.flip()
            #print(t1 - t0)
            if win.dt > frame_period_tol:
                dropped_frames.append([win.current_time - t_start, win.dt])

        rush(False)
        data_stack = stack(data_list)
        return data_stack, dropped_frames

    def feedback_loop(self):
        win = self.win
        device = self.device
        trial_player = self.trial_player
        data_list = []
        self.feedback_anim.start(win.current_time)
        while self.feedback_anim.is_playing or self.trial_player.is_playing:
            data = device.read()
            data_list.append(data.copy())
            self.feedback_anim.advance(win.current_time + win.frame_period)
            trial_player.advance(win.current_time + win.frame_period)
            self.draw()
            win.flip()

        # reset after feedback
        self.check.visible = False
        self.x.visible = False
        self.particle_burst.visible = False
        self.shadow.visible = False
        self.ball.visible = True
        self.ball2.visible = False

        return stack(data_list)

    def fade_which(self, track, sort):
        fade_track = track
        self.fade.visible = True
        fade_player = Player()
        fade_player.add(fade_track, 'a', self.fade.fill_color)

        fade_player.start(default_timer())
        while fade_player.is_playing:
            fade_player.advance(default_timer())
            self.draw()
            self.fade.draw(self.win.cam)
            self.win.flip()
        self.fade.visible = False
        if sort == 'in':
            self.countdown.start()
            while self.countdown.player.is_playing:
                self.draw()
                self.countdown.draw()
                self.win.flip()

    def fade_in(self):
        self.fade_which(Track([(0, 1.0), (1, 0)]), 'in')

    def fade_out(self):
        self.fade_which(Track([(0, 0.0), (1, 1)]), 'out')
