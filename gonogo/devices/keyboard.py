from toon.input.device import BaseDevice, Obs
import ctypes
from pynput import keyboard
import os
import contextlib
from time import sleep


# https://stackoverflow.com/questions/38487114/python-2-x-sleep-call-at-millisecond-level-on-windows
if os.name == 'nt':
    from ctypes import wintypes

    winmm = ctypes.WinDLL('winmm')

    class TIMECAPS(ctypes.Structure):
        _fields_ = (('wPeriodMin', wintypes.UINT),
                    ('wPeriodMax', wintypes.UINT))

    def _check_time_err(err, func, args):
        if err:
            raise ValueError('%s error %d' % (func.__name__, err))
        return args

    winmm.timeGetDevCaps.errcheck = _check_time_err
    winmm.timeBeginPeriod.errcheck = _check_time_err
    winmm.timeEndPeriod.errcheck = _check_time_err

    @contextlib.contextmanager
    def timer_resolution(msecs=0):
        caps = TIMECAPS()
        winmm.timeGetDevCaps(ctypes.byref(caps), ctypes.sizeof(caps))
        msecs = min(max(msecs, caps.wPeriodMin), caps.wPeriodMax)
        winmm.timeBeginPeriod(msecs)
        yield
        winmm.timeEndPeriod(msecs)
else:
    # dummy
    @contextlib.contextmanager
    def timer_resolution(msecs=0):
        yield


class Keyboard(BaseDevice):
    class Press(Obs):
        shape = (1,)
        ctype = bool

    class Index(Obs):
        shape = (1,)
        ctype = int

    sampling_frequency = 10

    def __init__(self, keys=None, **kwargs):
        if keys is None:
            raise ValueError('Specify keys.')
        self.keys = keys
        super(Keyboard, self).__init__(**kwargs)

    def enter(self):
        self.dev = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        self.data = []
        self._on = []
        self.dev.start()
        self.dev.wait()

    def read(self):
        if not self.data:
            return self.Returns()
        ret = self.data.copy()
        self.data = []
        with timer_resolution(1):
            sleep(0.005)
        return ret

    def on_press(self, key):
        time = self.clock()
        if isinstance(key, keyboard.Key):
            bl = key.name in self.keys and key.value not in self._on
            value = key.value
        else:
            bl = key.char in self.keys and key.char not in self._on
            value = key.char

        if bl:
            rets = self.Returns(press=self.Press(time, True),
                                index=self.Index(time, self.keys.index(value)))
            self.data.append(rets)
            self._on.append(value)

    def on_release(self, key):
        time = self.clock()
        if isinstance(key, keyboard.Key):
            bl = key.name in self.keys and key.value in self._on
            value = key.value
        else:
            bl = key.char in self.keys and key.char in self._on
            value = key.char

        if bl:
            rets = self.Returns(press=self.Press(time, False),
                                index=self.Index(time, self.keys.index(value)))
            self.data.append(rets)
            self._on.remove(value)

    def exit(self, *args):
        self.dev.stop()
        self.dev.join()
