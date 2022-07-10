from slic.devices.general.motor import Motor


class stage:

    def __init__(self, name=None, vonHamos_horiz_pv=None, vonHamos_vert_pv=None):
        self.name = name
        self.horiz = Motor(vonHamos_horiz_pv)
        self.vert = Motor(vonHamos_vert_pv)

    def get_adjustable_positions_str(self):
        ostr = "***** VonHamos motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



