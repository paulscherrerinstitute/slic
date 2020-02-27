from IPython import get_ipython

from ..devices.basedevice import BaseDevice


def printable_table(d):
    length = max(len(k) for k in d) + 1
    lines = ("{} {}".format((k+":").ljust(length), v) for k, v in d.items())
    return "\n".join(sorted(lines))


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

        return printable_table(res)



