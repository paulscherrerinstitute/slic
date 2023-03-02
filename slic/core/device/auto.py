from ..adjustable import Adjustable
from .device import Device
from .simpledevice import SimpleDevice


def auto(globals_dict, ID, **kwargs):
    """
    Return a new SimpleDevice with the Adjustables/Devices extracted from globals_dict
    globals_dict is expected to be the result of globals() from within ipython
    Thus, the intended usage is:
        overview = auto(globals(), "Overview")
    """
    res = {}
    for k, v in globals_dict.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, (Adjustable, Device)):
            continue
        res[k] = v
    return SimpleDevice(ID, **kwargs, **res)



