from ..devices_general.motors import MotorRecord
from ..devices_general.smaract import SmarActRecord
from epics import PV
from ..devices_general.delay_stage import DelayStage


class palm:
    def __init__(self, Id):
        self.Id = Id

        self.delay = MotorRecord(self.Id + "-M423:MOT")
        self.delayTime = DelayStage(self.delay)

    # 		self.delay2 = MotorRecord(self.Id+'-M422:MOT')
    #         self.delayTime2 = DelayStage(self.delay)

    def get_adjustable_positions_str(self):
        ostr = "***** PALM motor positions ******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(10) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()


class eo:
    def __init__(self, Id):
        self.Id = Id

        self.delay = MotorRecord(self.Id + "-M422:MOT")
        self.delayTime = DelayStage(self.delay)

    def get_adjustable_positions_str(self):
        ostr = "***** PALM EO sampling motor positions ******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(10) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()
