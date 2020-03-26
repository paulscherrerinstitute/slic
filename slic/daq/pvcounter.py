from time import sleep
import numpy as np
from epics import PV

from .counter import Counter



class PVCounter(Counter):

    def _acquire(self, *args, polling=False, **kwargs):
        if polling:
            epics_to_h5_polling(*args, **kwargs)
        else:
            epics_to_h5_triggered(*args, **kwargs)



def epics_to_h5_polling(filename, channels, n_pulses=100, wait_time=0.5):
    pvs = [PV(ch) for ch in channels]

    arrays = make_arrays(pvs, n_pulses)

    for ivalue in range(n_pulses):
        #TODO: What is the overhead here? Minimal wait_time? Run read out in thread(s)?
        for ichannel, pv in enumerate(pvs):
            arrays[ichannel][ivalue] = pv.value
        sleep(wait_time)

    write_to_h5(filename, channels, arrays)



def epics_to_h5_triggered(filename, channels, n_pulses=100, wait_time=0.5):
    pvs = [PV(ch) for ch in channels]

    n_channels = len(channels)
    counters = np.zeros(n_channels)

    arrays = make_arrays(pvs, n_pulses)


    def on_value_change(pv=None, ichannel=None, value=None, **kwargs):
        ivalue = counters[ichannel]
        arrays[ichannel][ivalue] = value

        counters[ichannel] += 1

        if counters[ichannel] == n_pulses:
            pv.clear_callbacks()


    for i, pv in enumerate(pvs):
        pv.add_callback(callback=on_value_change, pv=pv, ichannel=i)

    while not np.all(counters == n_pulses):
        sleep(wait_time)

    write_to_h5(filename, channels, arrays)



def make_arrays(pvs, n_pulses):
    arrays = []
    for pv in pvs:
        val = pv.value

        dtype = get_dtype(val)
        shape = get_shape(val)
        shape = (n_pulses,) + shape

        arr =  np.empty(shape, dtype)
        arrays.append(arr)

    return arrays


def get_dtype(v):
    if is_array(v):
        return v.dtype
    else:
        return type(v)

def get_shape(v):
    if is_array(v):
        return v.shape
    else:
        return tuple()

def is_array(v):
    return isinstance(v, np.ndarray)


def write_to_h5(filename, channels, arrays):
    if filename == "/dev/null":
        return

    with h5py.File(filename, "x") as f:
        for ch, arr in zip(channels, arrays):
            f.create_dataset(ch, data=arr)



