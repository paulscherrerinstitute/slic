from epics import PV

from slic.devices.general.motor import Motor
from ...general.smaract import SmarActAxis
from ...general.delay_stage import DelayStage


class Palm:

    def __init__(self, Id):
        self.Id = Id

        self._delayStg = Motor(self.Id + "-M552:MOT")
        self.delay = DelayStage(self._delayStg)

    def get_adjustable_positions_str(self):
        ostr = "*****Palm motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(10) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



