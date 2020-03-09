from datetime import datetime, timedelta
import os
import zmq

import data_api as dapi
from bsread.h5 import receive
from bsread.avail import dispatcher

from .acquisition import Acquisition
from .basecounter import BaseCounter
from .utils import can_create_file, fix_hdf5_filename



class BSCounter(BaseCounter):

    def __init__(self, default_channels=None, default_path="."):
        self.default_channels = default_channels
        self.default_path = default_path


    def acquire(self, filename=None, n_pulses=100, **kwargs):
        acq = lambda: self.h5(filename=filename, n_pulses=n_pulses, **kwargs)
        return Acquisition(acq, hold=False)


    def h5(self, filename=None, channels=None, n_pulses=None, use_default_path=True, queue_size=100, mode=zmq.SUB):
        if filename and use_default_path:
            filename = os.path.join(self.default_path, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        source = dispatcher.request_stream(channels)
        receive(source, filename, queue_size=queue_size, mode=mode, n_messages=n_pulses)


    def h5_db(self, filename=None, use_default_path=True, **kwargs):
        if filename and use_default_path:
            filename = os.path.join(self.default_path, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        data = self.db(**kwargs)
        data.to_hdf(filename, "/data")


    def db(self, channels=None, start_time_delta=None, end_time_delta=None):
        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        start_time_delta = start_time_delta if start_time_delta is not None else dict(seconds=0)
        end_time_delta   = end_time_delta   if end_time_delta   is not None else dict(seconds=1)

        start_time_delta = timedelta(**start_time_delta)
        end_time_delta   = timedelta(**end_time_delta)

        now   = datetime.now()
        end   = now - end_time_delta
        start = end - start_time_delta

        return dapi.get_data(channels=channels, start=start, end=end)



