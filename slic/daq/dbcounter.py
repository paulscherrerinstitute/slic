from datetime import datetime, timedelta

import data_api as dapi

from .counter import Counter



class DBCounter(Counter):

    def _acquire(self, *args, **kwargs):
        dapi_to_h5(*args, **kwargs)



def dapi_to_h5(filename, channels, **kwargs):
    data = dapi_get(channels, **kwargs)
    if filename != "/dev/null":
        data.to_hdf(filename, "/data")


def dapi_get(channels, start=None, end=None):
    start = start if start is not None else dict(seconds=0)
    end   = end   if end   is not None else dict(seconds=1)

    start_time_delta = timedelta(**start)
    end_time_delta   = timedelta(**end)

    now   = datetime.now()
    start = now + start_time_delta
    end   = start + end_time_delta

    return dapi.get_data(channels=channels, start=start, end=end)



