from epics import get_pv
from slic.utils.printing import printable_dict
from .adjustable import Adjustable


class PVEnumAdjustable(Adjustable):

    def __init__(self, pvname, ID=None, name=None, units=None, internal=False):
        self.pvname = pvname
        self.pv = pv = get_pv(pvname)

        ID = ID or pvname
        super().__init__(ID, name=name, units=units, internal=internal)

        self.states = Enum(pv.enum_strs)


    @property
    def units(self):
        units = self._units
        if units is not None:
            return units
        return self.pv.units

    @units.setter
    def units(self, value):
        self._units = value


    def get_current_value(self, as_number=False):
        as_string = not as_number
        return self.pv.get(as_string=as_string)

    def set_target_value(self, value):
        value = self.states.get(value)
        self.pv.put(value, wait=True, use_complete=True)

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



