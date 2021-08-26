from epics import PV

from slic.devices.general.motor import Motor
from slic.utils.eco_components.aliases import Alias


def addMotorToSelf(self, name=None, ID=None):
    try:
        self.__dict__[name] = Motor(ID, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (ID: {ID})")


class OffsetMirror:

    def __init__(self, name=None, ID=None, alias_namespace=None):
        self.ID = ID
        self.name = name
        self.alias = Alias(name)

        addMotorToSelf(self, ID=ID + ":W_X", name="x")
        addMotorToSelf(self, ID=ID + ":W_Y", name="y")
        addMotorToSelf(self, ID=ID + ":W_RX", name="rx")
        addMotorToSelf(self, ID=ID + ":W_RZ", name="rz")

    def out(self):
        pass

    def move_in(self):
        pass



