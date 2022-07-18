import numpy as np
from slic.utils import get_dtype, get_shape
from slic.utils.hastyepics import get_pv as PV


class PVDataStream:

    def __init__(self, name, wait_time=0.1):
        self.name = name
        self.wait_time = wait_time
        self.pv = PV(name)


    def record(self, n):
        pv = self.pv
        current = pv.get()

        shape = (n,) + get_shape(current)
        dtype = get_dtype(current)

        data = np.empty(shape=shape, dtype=dtype)
        index = 0
        running = True

        def on_value_change(value=None, **kwargs):
            nonlocal index
            nonlocal running
            data[index] = value
            index += 1
            if index == n:
                pv.clear_callbacks()
                running = False

        pv.add_callback(callback=on_value_change)

        while running:
            sleep(self.wait_time)

        return data



