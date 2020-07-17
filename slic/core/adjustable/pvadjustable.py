from types import SimpleNamespace
from epics import PV
from slic.core.task import Task
from .adjustable import Adjustable


class PvAdjustable(Adjustable):

    def __init__(self, pvname_setvalue, pvname_readback=None, accuracy=None, name=None):
        name = name or pvname_setvalue
        super().__init__(name)

        self.accuracy = accuracy

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback) if pvname_readback else pv_setvalue

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback
        )

        self.pvs = SimpleNamespace(
            setvalue = pv_setvalue,
            readback = pv_readback
        )


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.setvalue.get()

    def set_target_value(self, value, hold=False):
        def change():
            # use_complete=True enables status in PV.put_complete
            self.pvs.setvalue.put(value, wait=True, use_complete=True)
        self.current_task = task = Task(change, hold=hold)
        return task

    def is_moving(self):
        if self.accuracy is not None:
            setvalue = self.get_current_value(readback=False)
            readback = self.get_current_value(readback=True)
            delta = abs(setvalue - readback)
            return delta > self.accuracy
        else:
            return not self.pvs.setvalue.put_complete



