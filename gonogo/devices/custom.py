import hid
import struct
from toon.input import BaseDevice, Obs
from ctypes import c_uint16, c_uint32

import serial
from serial.tools import list_ports


class Custom2(BaseDevice):
    class Forces(Obs):
        shape = (2,)
        ctype = c_uint16

    class Photo(Obs):
        shape = (1,)
        ctype = c_uint16

    class Buttons(Obs):
        shape = (2,)
        ctype = bool

    def __init__(self, blocking=True, **kwargs):
        super(Custom2, self).__init__(**kwargs)
        self.nonblocking = not blocking
        self._device = None

    def __enter__(self):
        self._device = hid.device()
        dev_path = next((dev for dev in hid.enumerate()
                         if dev['vendor_id'] == 0x16c0 and dev['interface_number'] == 0), None)['path']
        self._device.open_path(dev_path)
        # TODO: nonblocking spin until data is empty, *then* move on
        self._device.set_nonblocking(self.nonblocking)
        return self

    def __exit__(self, *args):
        self._device.close()

    def read(self):
        data = self._device.read(10)
        time = self.clock()
        if data:
            data = struct.unpack('<HHHhh', bytearray(data))
            return self.Returns(photo=self.Photo(time, data[0]),
                                forces=self.Forces(time, data[1:3]),
                                buttons=self.Buttons(time, data[3:]))
        else:
            return None, None


class Custom(BaseDevice):
    class Forces(Obs):
        shape = (2,)
        ctype = c_uint16

    class Photo(Obs):
        shape = (1,)
        ctype = c_uint16

    class Buttons(Obs):
        shape = (2,)
        ctype = int

    class Times(Obs):
        shape = (1,)
        ctype = c_uint32

    def __init__(self, **kwargs):
        super(Custom, self).__init__(**kwargs)
        self._device = None

    def enter(self):
        ports = list_ports.comports()
        mydev = next((p.device for p in ports if p.pid == 1155))
        self._device = serial.Serial(mydev)
        try:
            self._device.set_low_latency_mode(True)  # pyserial from github
        except Exception:
            pass
            #print('Either not allowed to set the mode, or pyserial not up-to-date')
        self._device.write(b's')  # reset the timer on the teensy
        # TODO: nonblocking spin until data is empty, *then* move on

    def exit(self, *args):
        self._device.close()

    def read(self):
        data = self._device.read(64)
        time = self.clock()
        if data:
            data = struct.unpack('<LHHHhh', bytearray(data[:14]))
            return self.Returns(times=self.Times(time, data[0]),
                                photo=self.Photo(time, data[1]),
                                forces=self.Forces(time, data[2:4]),
                                buttons=self.Buttons(time, data[4:6]))
        else:
            return None, None
