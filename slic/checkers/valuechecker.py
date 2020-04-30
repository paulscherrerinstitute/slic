from .checker import Checker
from slic.task import Loop


class ValueChecker(Checker):

    def __init__(self, get_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_value = get_value
        self.task = None


    def current(self):
        return self.get_value()


    def start_counting(self):
        if self.task:
            return # don't start collecting twice

        def collect():
            value = self.current()
            self.data.append(value)

        self.task = Loop(collect, self.wait_time)


    def stop_counting(self):
        if not self.task:
            return # can only stop something, if we started it

        self.task.stop()
        self.task = None



