import numpy as np

from slic.core.adjustable import PVEnumAdjustable
from slic.devices.general.detectors_new import FeDigitizer, PvDataStream
from slic.devices.general.motor import Motor
from slic.utils.hastyepics import get_pv as PV


class SolidTargetDetectorPBPS:

    def __init__(self, pvname, VME_crate=None, link=None, channels={}, ch_up=12, ch_down=13, ch_left=15, ch_right=14, elog=None, name=None, calc=None, calc_calib={}):
        self.name = name
        self.pvname = pvname
        self.x_diodes = Motor(pvname + ":MOTOR_X1")
        self.y_diodes = Motor(pvname + ":MOTOR_Y1")
        self.target_y = Motor(pvname + ":MOTOR_PROBE")
        self.target = PVEnumAdjustable(pvname + ":PROBE_SP")
        if VME_crate:
            self.diode_up = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_up))
            self.diode_down = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_down))
            self.diode_left = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_left))
            self.diode_right = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_right))

        if channels:
            self.signal_up = PvDataStream(channels["up"])
            self.signal_down = PvDataStream(channels["down"])
            self.signal_left = PvDataStream(channels["left"])
            self.signal_right = PvDataStream(channels["right"])

        if calc:
            self.intensity = PvDataStream(calc["itot"])
            self.xpos = PvDataStream(calc["xpos"])
            self.ypos = PvDataStream(calc["ypos"])

    def get_calibration_values(self, seconds=5):
        self.x_diodes.set_target_value(0).wait()
        self.y_diodes.set_target_value(0).wait()
        ds = [self.signal_up, self.signal_down, self.signal_left, self.signal_right]
        aqs = [d.acquire(seconds=seconds) for d in ds]
        data = [aq.wait() for aq in aqs]
        mean = [np.mean(td) for td in data]
        std = [np.std(td) for td in data]
        norm_diodes = [1 / tm / 4 for tm in mean]
        return norm_diodes

    def set_calibration_values(self, norm_diodes):
        #this is now only for bernina when using the ioxos from sla
        channels = ["SLAAR21-LTIM01-EVR0:CALCI.INPG", "SLAAR21-LTIM01-EVR0:CALCI.INPH", "SLAAR21-LTIM01-EVR0:CALCI.INPF", "SLAAR21-LTIM01-EVR0:CALCI.INPE"]
        for tc, tv in zip(channels, norm_diodes):
            PV(tc).put(bytes(str(tv), "utf8"))
        channels = ["SLAAR21-LTIM01-EVR0:CALCX.INPE", "SLAAR21-LTIM01-EVR0:CALCX.INPF"]
        for tc, tv in zip(channels, norm_diodes[2:4]):
            PV(tc).put(bytes(str(tv), "utf8"))
        channels = ["SLAAR21-LTIM01-EVR0:CALCY.INPE", "SLAAR21-LTIM01-EVR0:CALCY.INPF"]
        for tc, tv in zip(channels, norm_diodes[0:2]):
            PV(tc).put(bytes(str(tv), "utf8"))

    def get_calibration_values_position(self, calib_intensities, seconds=5, motion_range=0.2):
        self.x_diodes.set_epics_limits(-motion_range / 2 - 0.1, +motion_range / 2 + 0.1)
        self.y_diodes.set_epics_limits(-motion_range / 2 - 0.1, +motion_range / 2 + 0.1)
        self.x_diodes.set_target_value(0).wait()
        self.y_diodes.set_target_value(0).wait()
        raw = []
        for pos in [motion_range / 2, -motion_range / 2]:
            self.x_diodes.set_target_value(pos).wait()
            aqs = [ts.acquire(seconds=seconds) for ts in [self.signal_left, self.signal_right]]
            vals = [np.mean(aq.wait()) * calib for aq, calib in zip(aqs, calib_intensities[0:2])]
            raw.append((vals[0] - vals[1]) / (vals[0] + vals[1]))
        grad = motion_range / np.diff(raw)[0]
        # xcalib = [np.diff(calib_intensities[0:2])[0]/np.sum(calib_intensities[0:2]), grad]
        xcalib = [0, grad]
        self.x_diodes.set_target_value(0).wait()
        raw = []
        for pos in [motion_range / 2, -motion_range / 2]:
            self.y_diodes.set_target_value(pos).wait()
            aqs = [ts.acquire(seconds=seconds) for ts in [self.signal_up, self.signal_down]]
            vals = [np.mean(aq.wait()) * calib for aq, calib in zip(aqs, calib_intensities[2:4])]
            raw.append((vals[0] - vals[1]) / (vals[0] + vals[1]))
        grad = motion_range / np.diff(raw)[0]
        # ycalib = [np.diff(calib_intensities[2:4])[0]/np.sum(calib_intensities[2:4]), grad]
        ycalib = [0, grad]
        self.y_diodes.set_target_value(0).wait()
        return xcalib, ycalib

    def set_calibration_values_position(self, xcalib, ycalib):
        channels = ["SLAAR21-LTIM01-EVR0:CALCX.INPJ", "SLAAR21-LTIM01-EVR0:CALCX.INPI"]
        # txcalib = [-1*xcalib[0],-1*xcalib[1]]
        for tc, tv in zip(channels, xcalib):
            PV(tc).put(bytes(str(tv), "utf8"))
        channels = ["SLAAR21-LTIM01-EVR0:CALCY.INPJ", "SLAAR21-LTIM01-EVR0:CALCY.INPI"]
        for tc, tv in zip(channels, ycalib):
            PV(tc).put(bytes(str(tv), "utf8"))

    def calibrate(self, seconds=5):
        c = self.get_calibration_values(seconds=seconds)
        self.set_calibration_values(c)
        xc, yc = self.get_calibration_values_position(c, seconds=seconds)
        self.set_calibration_values_position(xc, yc)

    def __repr__(self):
        s = f"**Intensity  monitor {self.name}**\n\n"

        s += f"Target in: {self.target.get_current_value().name}\n\n"
        try:
            sd = "**Biasd voltage**\n"
            sd += " - Diode up: %.4f\n" % (sdelf.diode_up.get_biasd())
            sd += " - Diode down: %.4f\n" % (sdelf.diode_down.get_biasd())
            sd += " - Diode left: %.4f\n" % (sdelf.diode_left.get_biasd())
            sd += " - Diode right: %.4f\n" % (sdelf.diode_right.get_biasd())
            sd += "\n"

            sd += "**Gain**\n"
            sd += " - Diode up: %i\n" % (sdelf.diode_up.gain.get())
            sd += " - Diode down: %i\n" % (sdelf.diode_down.gain.get())
            sd += " - Diode left: %i\n" % (sdelf.diode_left.gain.get())
            sd += " - Diode right: %i\n" % (sdelf.diode_right.gain.get())
            s += sd
        except:
            pass
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

        # SAROP21-CVME-PBPS:Lnk10Ch15-WD-gain



