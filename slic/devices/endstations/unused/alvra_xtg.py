from ..devices_general.smaract import SmarActRecord
from epics import PV


class XTG:

    def __init__(self, Id, alias_namespace=None):
        self.Id = Id

        ### sample smaract motors ###
        self.sx = SmarActRecord(Id + ":TRX3")
        self.sy = SmarActRecord(Id + ":TRY3")

        ### grating 1 motors ###
        self.g1x = SmarActRecord(Id + ":TRX1")
        self.g1y = SmarActRecord(Id + ":TRY1")
        self.g1z = SmarActRecord(Id + ":TRZ1")
        ### grating 2 motors ###
        self.g2x = SmarActRecord(Id + ":TRX2")
        self.g2y = SmarActRecord(Id + ":TRY2")
        self.g2z = SmarActRecord(Id + ":TRZ2")

    def get_adjustable_positions_str(self):
        ostr = "*****SmarAct motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(10) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



