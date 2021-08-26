from epics import PV
from time import sleep
import numpy as np

from slic.devices.general.motor import Motor
from slic.utils.eco_components.aliases import Alias


def addMotorToSelf(self, name=None, ID=None):
    try:
        self.__dict__[name] = Motor(ID, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (ID: {ID})")


class Pulsepick:

    def __init__(self, ID=None, evronoff=None, evrsrc=None, name=None):
        self.name = name
        self.alias = Alias(name)
        self.evrsrc = evrsrc
        self.evronoff = evronoff

        self.ID = ID
        self._openclose = PV(self.evronoff)
        self._evrsrc = PV(self.evrsrc)
        addMotorToSelf(self, ID=self.ID + ":MOTOR_X1", name="x")
        addMotorToSelf(self, ID=self.ID + ":MOTOR_Y1", name="y")

    def movein(self):
        self.x.set_target_value(4.45)
        self.y.set_target_value(-1.75)

    def moveout(self):
        self.x.set_target_value(-5)
        self.y.set_target_value(-1.75)

    def open(self):
        self._openclose.put(1)
        self._evrsrc.put(62)
        print("Opened Pulse Picker")

    def close(self):
        self._openclose.put(0)
        self._evrsrc.put(62)
        print("Closed Pulse Picker")

    def trigger(self):
        self._openclose.put(1)
        self._evrsrc.put(0)
        print("Set Pulse Picker to trigger (src 0 and output On)")

    def get_status(self):
        stat = self._evrsrc.get()
        if stat == 62 and self._openclose.get() == 1:
            return "open"
        if self._openclose.get() == 0:
            return "closed"
        else:
            return "unknown"

    def __repr__(self):
        return f"FEL pulse picker state {self.get_status()}."



