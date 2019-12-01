#from epics import PV


class PV:

    def __init__(self, *args, **kwargs):
        pass


def within(val, vmin, vmax):
    left  = True if vmin is None else (val > vmin)
    right = True if vmax is None else (val < vmax)
    return (left and right)


class PVChecker:

    def __init__(self, channel, vmin, vmax, wait_time):
        self.channel = channel
        self.pv = PV(channel)
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time

    def check(self):
        val = self.pv.get()
        return within(val, self.vmin, self.vmax)



