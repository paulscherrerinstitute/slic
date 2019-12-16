import sys

sys.path.append("..")
from ..general.motors import MotorRecord

from epics import PV
from slic.utils.eco_components.aliases import Alias


def addMotorRecordToSelf(self, name=None, Id=None):
    try:
        self.__dict__[name] = MotorRecord(Id, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (Id:{Id})")


class OffsetMirror:
    def __init__(self, name=None, Id=None, alias_namespace=None):
        self.Id = Id
        self.name = name
        self.alias = Alias(name)

        addMotorRecordToSelf(self, Id=Id + ":W_X", name="x")
        addMotorRecordToSelf(self, Id=Id + ":W_Y", name="y")
        addMotorRecordToSelf(self, Id=Id + ":W_RX", name="rx")
        addMotorRecordToSelf(self, Id=Id + ":W_RZ", name="rz")

    def out(self):
        pass

    def move_in(self):
        pass
