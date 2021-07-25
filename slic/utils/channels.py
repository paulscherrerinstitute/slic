import warnings


def load_channels(fname):
    out = set()
    with open(fname, "r") as f:
        for line in f:
            line = line.split("#")[0] # remove comments
            line = line.strip()
            if not line:
                continue
            out.add(line)
    return sorted(out)



message = """\
The class slic.utils.Channels is deprecated.
Please use, whichever appropriate, slic.core.acquisition.BSChannel, slic.core.acquisition.PVChannel or slic.utils.load_channels instead.
"""


class Channels(list):

    def __init__(self, fname):
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        chs = load_channels(fname)
        self.extend(chs)



