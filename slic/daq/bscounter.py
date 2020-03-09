from datetime import datetime, timedelta
import os
import zmq

from bsread.h5 import receive
from bsread.avail import dispatcher

from .acquisition import Acquisition
from .basecounter import BaseCounter
from .utils import can_create_file, fix_hdf5_filename



def bsread_to_h5(filename, channels, n_pulses=100, queue_size=100, mode=zmq.SUB):
    source = dispatcher.request_stream(channels)
    receive(source, filename, queue_size=queue_size, mode=mode, n_messages=n_pulses)



class BSCounter(BaseCounter):

    def __init__(self, default_channels=None, default_path="."):
        self.default_channels = default_channels
        self.default_path = default_path


    def acquire(self, filename=None, channels=None, use_default_path=True, **kwargs):
        if filename and use_default_path:
            filename = os.path.join(self.default_path, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        acq = lambda: bsread_to_h5(filename, channels, **kwargs)
        return Acquisition(acq, hold=False)



