from slic.devices.general.motor import Motor
from slic.utils.deprecated.aliases import Alias, append_object_to_object


class stage:

    def __init__(self, name=None, vonHamos_horiz_pv=None, vonHamos_vert_pv=None):
        self.name = name
        self.alias = Alias(name)
        append_object_to_object(self, Motor, vonHamos_horiz_pv, name="horiz")
        append_object_to_object(self, Motor, vonHamos_vert_pv, name="vert")

    def get_adjustable_positions_str(self):
        ostr = "***** VonHamos motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



