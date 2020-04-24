from .checker import Checker
from slic.runners import LoopRunner


class ValueChecker(Checker):

    def __init__(self, get_value, vmin, vmax, wait_time, required_fraction):
        self.get_value = get_value
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time
        self.required_fraction = required_fraction

        self.data = []
        self.runner = None


    def current(self):
        return self.get_value()


    def start_counting(self):
        if self.runner:
            return # don't start collecting twice

        def collect():
            value = self.current()
            self.data.append(value)

        self.runner = LoopRunner(collect, self.wait_time)


    def stop_counting(self):
        if not self.runner:
            return # can only stop something, if we started it

        self.runner.stop()
        self.runner = None



