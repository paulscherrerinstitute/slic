from IPython import get_ipython

from .utils import singleton
from .printing import printable_dict
from ..devices.basedevice import BaseDevice


@singleton
class devices:

    def __repr__(self):
        ipy = get_ipython()
        if ipy is None:
            return "The device list only works within ipython"

        ns = ipy.user_ns
        res = {}
        for k, v in ns.items():
            if k.startswith("_"):
                # skip ipython's numbered In/Out
                continue
            if isinstance(v, BaseDevice):
                try:
                    doc = v.description
                except AttributeError:
                    doc = v.__doc__ or v.name or v.Id
                res[k] = doc

        return printable_dict(res)



