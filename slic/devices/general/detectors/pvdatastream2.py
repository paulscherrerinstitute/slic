from slic.utils.hastyepics import get_pv as PV

from .buffer import Buffer
from .timer import Timer


class PVDataStream:

    def __init__(self, name, wait_time=0.1):
        self.name = name
        self.wait_time = wait_time
        self.pv = PV(name)


    def record(self, n, seconds=None):
        pv = self.pv

        current = pv.get()
        buf = Buffer.from_example(n, current)
        tim = Timer(seconds)

        running = True

        def on_value_change(value=None, **kwargs):
            nonlocal running
            buf.append(value)
            if buf.is_full or tim.is_done:
                pv.clear_callbacks()
                running = False

        pv.add_callback(callback=on_value_change)

        while running:
            sleep(self.wait_time)

        return buf.data



