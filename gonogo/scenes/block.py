import csv
import json
from abc import ABCMeta, abstractmethod
from datetime import datetime
import os
from gonogo.utils import NumpyEncoder

class Block(metaclass=ABCMeta):
    @property
    @abstractmethod
    def expected_handler_keys(self):
        # keys that the Block is expecting the block_handler to have
        # or else
        pass

    @property
    @abstractmethod
    def trial_data_keys(self):
        # expected summary data output per-trial (in addition to the block handler keys)
        pass

    def __init__(self, win, block_handler, device, user_settings):
        diff = set(self.expected_handler_keys).difference(block_handler.keys)
        if len(diff) > 0:
            raise ValueError('Missing keys from block_handler: [%s]' % ', '.join(diff))
        self.win = win
        self.block_handler = block_handler
        self.device = device
        self.user_settings = user_settings
        self._trial_counter = 0
        self.datetime = ''  # implementations should get the datetime when run() is called
        # self.trial_data = dict.fromkeys(self.trial_data_keys + self.expected_handler_keys)

        # block path
        self.block_path = os.path.join(user_settings['subj_path'],
                                       block_handler.name,
                                       'block%s' % block_handler.text_dict['block_key'])

        os.makedirs(self.block_path, exist_ok=True)
        os.makedirs(os.path.join(self.block_path, 'traces'), exist_ok=True)
        os.makedirs(os.path.join(self.block_path, 'dropped_frames'), exist_ok=True)
        # dump original block settings
        sets_path = os.path.join(self.block_path, 'block_settings.json')
        with open(sets_path, 'w') as f:
            json.dump(block_handler.text_dict, f, indent=2, cls=NumpyEncoder)

    def write_data(self, summary, long_data, ref_time, dropped_frames):
        fieldnames = summary.keys()
        if self._trial_counter < 1:
            sname = 'summary_%s_%s_%s.csv' % (self.user_settings['id'],
                                              self.block_handler.name,
                                              self.datetime)
            self.block_summary_name = os.path.join(self.block_path, sname)
            with open(self.block_summary_name, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames)
                writer.writeheader()
        with open(self.block_summary_name, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(summary)

        # subtract off ref_time so time is relative to trial start
        trace_path = os.path.join(self.block_path, 'traces', 'traces_trial%i.json' % self._trial_counter)
        out_dct = {f: {'time': None, 'data': None} for f in long_data._fields}
        for field in long_data._fields:
            # extract particular data
            dat = getattr(long_data, field)
            if dat is not None:
                out_dct[field]['time'] = (dat.time - ref_time).tolist()
                out_dct[field]['data'] = dat.tolist()
        with open(trace_path, 'w') as f:
            json.dump(out_dct, f)

        # write any dropped frames
        dropped_path = os.path.join(self.block_path, 'dropped_frames', 'dropped_frames_trial%i.json' % self._trial_counter)
        with open(dropped_path, 'w') as f:
            json.dump(dropped_frames, f, indent=2)
        self._trial_counter += 1
