from IPython import get_ipython

from pathlib import Path

from .printing import printable_dict
from ..devices.basedevice import BaseDevice

import json


def json_dump(what, filename):
    with open(filename, "w") as f:
        json.dump(what, f, indent=4, sort_keys=True)



def make_dir(p):
    p = Path(p)
    if p.exists():
        return
    printable = p.absolute().as_posix()
    print(f"Path \"{printable}\" does not exist, will try to create it...")
    p.mkdir(parents=True)
    p.chmod(0o775)



def singleton(cls):
    return cls()


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
                    doc = v.__doc__
                res[k] = doc

        return printable_dict(res)



