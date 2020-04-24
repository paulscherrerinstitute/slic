from epics import PV

from .checker import Checker


class PVChecker(Checker):

    def __init__(self, channel, vmin, vmax, wait_time, required_fraction):
        self.channel = channel
        self.pv = PV(channel)
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time
        self.required_fraction = required_fraction

        self.data = []


    def current(self):
        return self.pv.get()


    def start_counting(self):
        def collect(value=None, **kwargs):
            self.data.append(value)

        self.pv.clear_callbacks() # add callback only once
        self.pv.add_callback(callback=collect)


    def stop_counting(self):
        self.pv.clear_callbacks()



