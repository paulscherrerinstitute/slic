from epics import PV
from .sensor import Sensor


class PVSensor(Sensor):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)
        self.pv = PV(ID)
        self._cb_index = None


    #TODO: using a similar block in PVAdjustable, Motor, ... already

    @property
    def units(self):
        units = self._units
        if units is not None:
            return units
        return self.pv.units

    @units.setter
    def units(self, value):
        self._units = value


    def get_current_value(self):
        return self.pv.get()


    def start(self):
        if self._cb_index is not None:
            print("already running")
            return
        self._cb_index = self.pv.add_callback(self._collect_cb)

    def stop(self):
        if self._cb_index is None:
            print("not started yet")
            return
        self.pv.remove_callback(self._cb_index)
        self._cb_index = None

    def _collect_cb(self, value=None, **kwargs):
        self._collect(value)



