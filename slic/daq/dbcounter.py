from datetime import datetime, timedelta

import data_api as dapi

from .counter import Counter



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



class DBCounter(Counter):

    def _acquire(self, *args, **kwargs):
        dapi_to_h5(*args, **kwargs)



