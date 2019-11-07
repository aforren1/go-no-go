from psychtoolbox import PsychHID as hid
from psychtoolbox import WaitSecs as wait_secs
from toon.input.device import BaseDevice, Obs


class PtbKeyboard(BaseDevice):
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
        self.kbd = hid('Devices', 2)[0]['index']  # master keyboard
        super().__init__(**kwargs)

    def enter(self):
        # make sure the DLLs/SOs is loaded
        hid()
        wait_secs(0.001)
        pass

    def read(self):
        key_is_down, ptb_time, data = hid('KbCheck', self.kbd)  # TODO: sub-indices (need keycode mapping)
        time = self.clock()
        # sleep ~0.75ms (so our 1kHz devices will be happy)
        # WaitSecs is *way* better than time.sleep (linux test below)
        # and we should use WaitSecs('UntilTime', ...) when possible
        # >>> timethat('ws(0.00075)', number=int(1e4))
        # ws(0.00075)                                                  751.53160 µs
        # >>> timethat('sleep(0.00075)', number=int(1e4))
        # sleep(0.00075)                                               920.57796 µs

        wait_secs('WaitUntil', ptb_time + 0.0008)
        # send data

    def exit(self, *args):
        pass
