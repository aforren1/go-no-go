import atexit
import wave

import numpy as np
import psychtoolbox as ptb
from psychtoolbox import PsychPortAudio as ppa

# master singleton soundcard
soundcard = None
# rather than reloading the sound each time (and using
# lots of slaves), keep a ref to the currently loaded ones
sound_cache = {}

ppa('Verbosity', 1)  # turn off everything but errors (which should raise exceptions anyway?)


def Soundcard():
    global soundcard
    if soundcard is None:
        # arg meanings
        # None-default device
        # 9-playback only, master
        # 2-full control over soundcard
        soundcard = ppa('Open', None, 9, 2, 44100)
        ppa('Start', soundcard)
        atexit.register(ppa, 'Close')
        atexit.register(ppa, 'Stop', soundcard)
    return soundcard


def rescale(values, old_min=-0.5, old_max=0.5, new_min=-0.5, new_max=0.5):
    return ((values - old_min)/(old_max - old_min)) * (new_max - new_min) + new_min


class Sound(object):

    @classmethod
    def from_file(cls, filename):
        with wave.open(filename, 'rb') as f:
            file_rate = f.getframerate()
            n_channels = f.getnchannels()
            raw_data = f.readframes(-1)
        data = np.frombuffer(raw_data, dtype='int16')/(2**16)
        data = rescale(data, old_min=min(data), old_max=max(data))
        data = data.reshape(-1, n_channels)
        return cls(data, file_rate)

    def __init__(self, data, file_rate):
        self._state = 'stop'
        soundcard = Soundcard()
        status = ppa('GetStatus', soundcard)
        data = np.atleast_2d(data)
        # catch if input shape is flipped around (should be nx2, not 2xn)
        if data.shape[0] < data.shape[1]:
            data = data.T
        hsh = hash(data.tostring())
        if hsh not in sound_cache.keys():
            # one handle+buffer per sound
            self.handle = ppa('OpenSlave', soundcard, 1)
            sample_rate = status['SampleRate']
            # resample sound data (linear interpolation)
            duration = data.shape[0]/file_rate  # time in sec (samples/(samples/sec))
            x_old = np.arange(0, duration, 1/file_rate)
            x_new = np.arange(0, duration, 1/sample_rate)
            data_new = np.zeros((x_new.shape[0], 2))
            data_new[:, 0] = np.interp(x_new, x_old, data[:, 0])
            # fix mono
            if data.shape[1] < 2:
                data_new[:, 1] = data_new[:, 0]
            else:  # assume stereo?
                data_new[:, 1] = np.interp(x_new, x_old, data[:, 1])
            ppa('FillBuffer', self.handle, data_new)
            sound_cache[hsh] = self.handle
        else:
            self.handle = sound_cache[hsh]

    def play(self):
        if self.state != 'play':
            ppa('Start', self.handle)

    def stop(self):
        ppa('Stop', self.handle)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value == 'play':
            self.play()
        elif value == 'stop':
            self.stop()
        else:
            raise ValueError('Invalid state.')
        self._state = value


if __name__ == '__main__':
    from time import sleep
    from pkg_resources import resource_filename as rf
    coin = rf('gonogo', '/resources/sound/coin.wav')
    buzz = rf('gonogo', '/resources/sound/buzz.wav')
    blop = rf('gonogo', '/resources/sound/blop.wav')
    snd = Sound.from_file(coin)
    snd5 = Sound.from_file(buzz)
    print('start')
    snd.play()
    sleep(1)
    snd.stop()
    snd2 = Sound.from_file(coin)
    snd6 = Sound.from_file(blop)

    fs = 16000
    freq = 400
    length = 0.3 * fs
    xx = np.arange(0, length)
    x = np.sin((2 * np.pi * freq * xx)/fs) * 0.25
    snd3 = Sound(x, fs)
    snd4 = Sound(x, fs)

    assert(snd.handle == snd2.handle)
    assert(snd3.handle == snd4.handle)
    print(sound_cache)
    snd3.play()
    for i in range(2):
        snd6.play()
        snd.state = 'play'
        sleep(0.2)
        snd2.play()
        sleep(0.2)
    snd5.play()
    sleep(1)
