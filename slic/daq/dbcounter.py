from datetime import datetime, timedelta
import os
import zmq

import data_api as dapi

from .acquisition import Acquisition
from .basecounter import BaseCounter
from .utils import can_create_file, fix_hdf5_filename



def dapi_to_h5(filename, channels, **kwargs):
    data = dapi_get(channels, **kwargs)
    data.to_hdf(filename, "/data")


def dapi_get(channels, start_time_delta=None, end_time_delta=None):
    start_time_delta = start_time_delta if start_time_delta is not None else dict(seconds=0)
    end_time_delta   = end_time_delta   if end_time_delta   is not None else dict(seconds=1)

    start_time_delta = timedelta(**start_time_delta)
    end_time_delta   = timedelta(**end_time_delta)

    now   = datetime.now()
    end   = now - end_time_delta
    start = end - start_time_delta

    return dapi.get_data(channels=channels, start=start, end=end)



class DBCounter(BaseCounter):

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

        acq = lambda: dapi_to_h5(filename, channels, **kwargs)
        return Acquisition(acq, hold=False)



