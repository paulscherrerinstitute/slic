from epics import PV
from slic.core.task import Task
from slic.utils.printing import printable_dict
from .adjustable import Adjustable


class PVEnumAdjustable(Adjustable):

    def __init__(self, pvname, name=None):
        name = name or pvname
        super().__init__(name)

        self.pv = PV(pvname)
        self.states = Enum(self.pv.enum_strs)


    def get_current_value(self, as_number=False):
        as_string = not as_number
        return self.pv.get(as_string=as_string)

    def set_target_value(self, value, hold=False):
        value = self.states.get(value)
        change = lambda: self.pv.put(value, wait=True, use_complete=True)
        self.current_task = task = Task(change, hold=hold)
        return task

    def is_moving(self):
        return not self.pv.put_complete



class Enum:

    def __init__(self, seq):
        self.data = {s:n for n, s in enumerate(seq)}

    def get(self, value):
        if value not in self.data.values():
            value = self.data[value]
        return value

    def __repr__(self):
        return printable_dict(self.data)



