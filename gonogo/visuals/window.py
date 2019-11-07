# this needs to happen before window is imported
# see moderngl examples
import atexit
import platform
import sys

import moderngl as mgl
import pyglet
from toon.input import mono_clock

from gonogo.constants import gray, dark_gray
from gonogo.visuals.projection import height_ortho
from mglg.graphics.camera import Camera
from mglg.math.vector import Vector4f

pyglet.options['debug_gl'] = False

# something something core context Macs
if platform.system() == 'Darwin':
    pyglet.options['shadow_window'] = False

# TODO: https://community.khronos.org/t/opengl-latency/37571/8
# https://gamedev.stackexchange.com/questions/69305/how-long-does-it-take-for-opengl-to-actually-update-the-screen
# https://stackoverflow.com/questions/31793228/osx-pushing-pixels-to-screen-with-minimum-latency
# http://emulation.gametechwiki.com/index.php/Input_lag

# not called "Window" to avoid conflict w/ pyglet proper


class ExpWindow(object):
    def __init__(self, background_color=dark_gray, clock=mono_clock.get_time):
        # TODO: if committing to moderngl, make & store the context here?
        # lazy load, partially to avoid auto-formatter that wants to
        # do imports, *then* dict setting
        from pyglet import gl
        from pyglet.window import Window

        self._background_color = Vector4f(background_color)
        self.clock = clock
        self.current_time = 0
        self.prev_time = 0
        # can bump down `samples` if performance is hurting
        config = gl.Config(depth_size=0, double_buffer=True,
                           alpha_size=8, sample_buffers=1,
                           samples=4, vsync=False,
                           major_version=3, minor_version=3)
        display = pyglet.canvas.get_display()
        screen = display.get_screens()[0]
        self._win = Window(resizable=False, fullscreen=True,
                           screen=screen, config=config,
                           style='borderless', vsync=True)

        self._win.event(self.on_key_press)
        atexit.register(self._on_close)
        self.context = mgl.create_context(require=int('%i%i0' % (config.major_version,
                                                                 config.minor_version)))
        self.context.viewport = (0, 0, self.width, self.height)
        self.context.enable(mgl.BLEND)
        self.frame_period  # do this before we've drawn anything
        # in principle, should be disconnected from the window
        # but we're saving time & mental energy
        self.cam = Camera(projection=height_ortho(self.width, self.height))

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys.exit(1)

    def _on_close(self):
        if self._win.context:
            self._win.close()

    def flip(self):
        self._win.switch_to()
        self._win.dispatch_events()
        self._win.flip()
        self.context.clear(*self._background_color)
        # gl.glBegin(gl.GL_POINTS)
        # gl.glColor4f(0, 0, 0, 0)
        # gl.glVertex2i(10, 10)
        # gl.glEnd()
        # gl.glFinish()  # force GL stuff to finish (but blocks CPU until then)
        current_time = self.clock()
        self.prev_time = self.current_time
        self.current_time = current_time
        return self.current_time

    def close(self):
        self._win.close()

    @property
    def dt(self):
        return self.current_time - self.prev_time

    def set_mouse_visible(self, val):
        self._win.set_mouse_visible(val)

    @property
    def width(self):
        return self._win.width

    @property
    def height(self):
        return self._win.height

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, val):
        if len(val) != 4:
            raise ValueError('Background color must be RGBA.')
        self._background_color.xyzw = val

    @property
    def frame_period(self):
        # get a whole-number version of the frame period
        # very coarse and fragile, should get this from the
        # the video mode, e.g. glfw.get_video_mode
        if not hasattr(self, '_frame_period'):
            possible = [60.0, 144.0]  # TODO: infer from machine...
            vals = []
            for _ in range(30):
                self.flip()
                vals.append(self.dt)
            # chop off the first few, which are not reflective of the
            # "real" FPS
            avg = 1/(sum(vals[5:])/float(len(vals[5:])))
            dff = [abs(avg - p) for p in possible]
            fps = [v for v, d in zip(possible, dff) if d == min(dff)]
            if not len(fps):
                self._frame_period = 1/60.0  # default
            else:
                self._frame_period = 1/fps[0]
        return self._frame_period


if __name__ == '__main__':
    from timeit import default_timer
    t0 = default_timer()
    win = ExpWindow()
    print('Init time: %4.4f' % (default_timer() - t0))
    print('Frame period: %4.4f' % win.frame_period)
    while default_timer() - t0 < 3:
        win.flip()
        if win.dt > 0.026:
            print(win.dt)
    win.background_color = (1, 0.5, 0.6, 0.1)
    while True:
        win.flip()
        if win.dt > 0.026:
            print(win.dt)
