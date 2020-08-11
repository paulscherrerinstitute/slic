from slic.utils import typename
from slic.core.task import Task
from .baseadjustable import BaseAdjustable
from .convenience import SpecConvenience


class Adjustable(BaseAdjustable, SpecConvenience):

    def __init__(self, name=None, units=None):
        self.name = name
        self.units = units
        self.current_task = None


    def _as_task(self, *args, **kwargs):
        self.current_task = task = Task(*args, **kwargs)
        return task

    def wait(self):
        if self.current_task:
            return self.current_task.wait()

    def stop(self):
        if self.current_task:
            return self.current_task.stop()


    def __call__(self, value=None):
        if value is not None:
            return self.set_target_value(value)
        else:
            return self.get_current_value()

    def set(self, *args, **kwargs):
        return self.set_target_value(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    @property
    def moving(self):
        return self.is_moving()


    def __repr__(self):
        tname = typename(self)
        name = self.name
        units = self.units
        value = self.get_current_value()

        name  = f"{tname} \"{name}\"" if name  is not None else tname
        value = f"{value} {units}"    if units is not None else value

        return f"{name} at {value}"



class AdjustableError(Exception):
    pass



