from slic.devices.general.motor import Motor
from slic.utils.eco_epics.utilities_epics import EnumWrapper
from ..general.detectors import FeDigitizer


class GasDetector:

    def __init__(self):
        pass


class SolidTargetDetectorPBPS:

    def __init__(self, ID, VME_crate=None, link=None, ch_up=12, ch_down=13, ch_left=15, ch_right=14, elog=None, z_undulator=None, description=None):
        self.ID = ID
        self.x_diode = Motor(ID + ":MOTOR_X1")
        self.y_diode = Motor(ID + ":MOTOR_Y1")
        self.y_target = Motor(ID + ":MOTOR_PROBE")
        self.target = EnumWrapper(ID + ":PROBE_SP")
        if VME_crate:
            self.diode_up = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_up))
            self.diode_down = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_down))
            self.diode_left = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_left))
            self.diode_right = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_right))

    def __repr__(self):
        s = "**Intensity  monitor**\n\n"

        s += "Target: " + (self.target.get_name()) + "\n\n"

        s += "**Bias voltage**\n"
        s += " - Diode up: %.4f\n" % (self.diode_up.get_bias())
        s += " - Diode down: %.4f\n" % (self.diode_down.get_bias())
        s += " - Diode left: %.4f\n" % (self.diode_left.get_bias())
        s += " - Diode right: %.4f\n" % (self.diode_right.get_bias())
        s += "\n"

        s += "**Gain**\n"
        s += " - Diode up: %i\n" % (self.diode_up.gain.get())
        s += " - Diode down: %i\n" % (self.diode_down.gain.get())
        s += " - Diode left: %i\n" % (self.diode_left.gain.get())
        s += " - Diode right: %i\n" % (self.diode_right.gain.get())
        return s

    def set_gains(self, value):
        try:
            self.diode_up.gain.set(value)
            self.diode_down.gain.set(value)
            self.diode_left.gain.set(value)
            self.diode_right.gain.set(value)
        except:
            print("No diodes configured, can not change any gain!")

    def get_available_gains(self):
        try:
            nu = self.diode_up.gain.names
            nd = self.diode_down.gain.names
            nl = self.diode_left.gain.names
            nr = self.diode_right.gain.names
            assert nu == nd == nl == nr, "NB: the gain options of the four diodes are not equal!!!"
            return nu
        except:
            print("No diodes configured, can not change any gain!")

    def get_gains(self):
        try:
            gains = dict()
            gains["up"] = (self.diode_up.gain.get_name(), self.diode_up.gain.get())
            gains["down"] = (self.diode_down.gain.get_name(), self.diode_down.gain.get())
            gains["left"] = (self.diode_left.gain.get_name(), self.diode_left.gain.get())
            gains["right"] = (self.diode_right.gain.get_name(), self.diode_right.gain.get())
            return gains
        except:
            print("No diodes configured, can not change any gain!")

        #SAROP21-CVME-PBPS:Lnk10Ch15-WD-gain



