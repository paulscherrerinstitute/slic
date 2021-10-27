from random import random
from time import sleep
from .adjustable import Adjustable


DELTA_T = 0.1 # sec


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, jitter=False, process_time=0, ID="DUMMY", name="Dummy", units=None):
        super().__init__(ID, name=name, units=units)
        self._current_value = initial_value
        self._jitter = jitter
        self._process_time = process_time
        self._running = False

    def get_current_value(self):
        value = self._current_value
        jitter = self._jitter
        if jitter:
            value += plus_minus() * float(jitter)
        return value


    def set_target_value(self, value):
        start_value = self._current_value
        process_time = self._process_time

        nsteps = int(process_time / DELTA_T)
        nsteps = max(1, nsteps)

        distance = value - start_value
        delta_value = distance / nsteps
        delta_time = process_time / nsteps

        self._running = True

        for i in range(nsteps):
            if not self._running:
                print(repr(self))
                return
            sleep(delta_time)
            self._current_value += delta_value

        # avoid rounding errors
        self._current_value = value

        self._running = False

        print(repr(self))


    def stop(self):
        self._running = False


    def is_moving(self):
        return self._running



def plus_minus():
    return 2 * random() - 1



