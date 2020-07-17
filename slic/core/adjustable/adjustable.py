from slic.utils import typename
from .baseadjustable import BaseAdjustable
from .convenience import SpecConvenience


class Adjustable(BaseAdjustable, SpecConvenience):

    def __init__(self, name=None):
        self.name = name
        self.current_task = None

    def set(self, *args, **kwargs):
        return self.set_target_value(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    @property
    def moving(self):
        return self.is_moving()

    def __repr__(self):
        name = self.name or typename(self)
        value = self.get_current_value()
        return "{} at {}".format(name, value)



#TODO handle Task creation only here, not in every subclass
