from epics import PV

from .condition import Condition


class PVCondition(Condition):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel
        self.pv = PV(channel)


    def current(self):
        return self.pv.get()


    def start_counting(self):
        def collect(value=None, **kwargs):
            self.data.append(value)

        self.pv.clear_callbacks() # add callback only once
        self.pv.add_callback(callback=collect)


    def stop_counting(self):
        self.pv.clear_callbacks()



