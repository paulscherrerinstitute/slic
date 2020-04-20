from epics import PV
from time import sleep

from .utils import within


class PVChecker:

    def __init__(self, channel, vmin, vmax, wait_time):
        self.channel = channel
        self.pv = PV(channel)
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time

    def check(self):
        val = self.current()
        return within(val, self.vmin, self.vmax)

    def current(self):
        return self.pv.get()

    def sleep(self):
        sleep(self.wait_time)



