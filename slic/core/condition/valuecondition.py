from slic.core.task import Loop

from .condition import Condition


class ValueCondition(Condition):

    def __init__(self, get_value, check_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_value = get_value
        self.check_time = check_time
        self.task = None


    def current(self):
        return self.get_value()


    def start_counting(self):
        if self.task:
            return # don't start collecting twice

        def collect():
            value = self.current()
            self.data.append(value)

        self.task = Loop(collect, self.check_time, hold=False)


    def stop_counting(self):
        if not self.task:
            return # can only stop something, if we started it

        self.task.stop()
        self.task = None



