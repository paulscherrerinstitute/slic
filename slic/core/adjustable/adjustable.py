from slic.utils import typename
from slic.utils.debug import Traceable
from slic.core.task import TaskProducer
from .baseadjustable import BaseAdjustable
from .error import AdjustableError
from .convenience import SpecConvenience, NumericConvenience
from .limited import Limited


class Adjustable(BaseAdjustable, TaskProducer, SpecConvenience, NumericConvenience, Limited, Traceable):

    stop = None #TODO: might be better to make this callable

    def __init__(self, ID, name=None, units=None, internal=False, limit_low=None, limit_high=None):
        self.ID = ID
        self.name = name or ID
        self.units = units
        self.internal = internal

        # The following allows a subclass to implement the methods that are actually called by a user.
        # The methods then are wrapped here to provide extra functionality (producing tasks, checking limits).

        self.set_target_value, _start, self.stop, self.wait =\
            self._task_producer(self.set_target_value, stopper=self.stop)

        self.set_limits(limit_low, limit_high)
        self.set_target_value = self._with_check_limits(self.set_target_value)


    def tweak(self, delta, *args, **kwargs):
        value = self.get_current_value()
        value += delta
        return self.set_target_value(value, *args, **kwargs)


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
        name  = self._printable_name()
        value = self._printable_value()
        return f"{name} at {value}"

    def __str__(self):
        return self._printable_value()

    def _printable_name(self):
        tname = typename(self)
        name = self.name
        return f"{tname} \"{name}\"" if name is not None else tname

    def _printable_value(self):
        value = self.get_current_value()
        units = self.units
        if units is None:
            return str(value)
        if units.casefold() in ["deg", "°"]:
            return f"{value}°"
        return f"{value} {units}"



