import numpy as np

from slic.utils.hastyepics import get_pv as PV


class PVDataStream:

    def __init__(self, name, wait_time=0.1):
        self.name = name
        self.wait_time = wait_time
        self.pv = PV(name)


    def record(self, n):
        pv = self.pv

        data = []
        running = True

        def on_value_change(value=None, **kwargs):
            nonlocal running
            data.append(value)
            if len(data) == n:
                pv.clear_callbacks()
                running = False

        pv.add_callback(callback=on_value_change)

        while running:
            sleep(self.wait_time)

        return np.array(data)



