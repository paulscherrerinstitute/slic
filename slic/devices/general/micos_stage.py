from slic.devices.general.motor import Motor
from slic.utils.deprecated.aliases import Alias, append_object_to_object


def addMotorToSelf(self, name=None, ID=None):
    try:
        self.__dict__[name] = Motor(ID, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (ID: {ID})")

        self.ID = ID
        self.name = name
        self.alias = Alias(name)


class stage:

    def __init__(self, name=None, vonHamos_horiz_pv=None, vonHamos_vert_pv=None):
        self.name = name
        self.alias = Alias(name)
        addMotorToSelf(self, ID=vonHamos_horiz_pv, name="horiz")
        addMotorToSelf(self, ID=vonHamos_vert_pv, name="vert")

    def get_adjustable_positions_str(self):
        ostr = "***** VonHamos motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



