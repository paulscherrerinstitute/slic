from ..devices_general.smaract import SmarActAxis
from epics import PV


class XTG:

    def __init__(self, ID, alias_namespace=None):
        self.ID = ID

        ### sample smaract motors ###
        self.sx = SmarActAxis(ID + ":TRX3")
        self.sy = SmarActAxis(ID + ":TRY3")

        ### grating 1 motors ###
        self.g1x = SmarActAxis(ID + ":TRX1")
        self.g1y = SmarActAxis(ID + ":TRY1")
        self.g1z = SmarActAxis(ID + ":TRZ1")
        ### grating 2 motors ###
        self.g2x = SmarActAxis(ID + ":TRX2")
        self.g2y = SmarActAxis(ID + ":TRY2")
        self.g2z = SmarActAxis(ID + ":TRZ2")

    def get_adjustable_positions_str(self):
        ostr = "*****SmarAct motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(10) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



