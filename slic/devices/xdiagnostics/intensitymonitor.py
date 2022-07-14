from collections import defaultdict
import numpy as np

from slic.core.adjustable import PVEnumAdjustable
from slic.core.device import Device
from slic.devices.general.detectors_new import FeDigitizer, PvDataStream
from slic.devices.general.motor import Motor
from slic.utils.hastyepics import get_pv as PV
from slic.utils.printing import format_header, printable_dict_of_dicts


class IntensityMonitorPBPS(Device):

    def __init__(self, ID,
        vme_crate=None, link=9, ch_up=12, ch_down=13, ch_right=14, ch_left=15, # -> DiodeArray
        calib_channels=None, # -> Calibrator
        calc_channels=None, # -> CalcIntensity
        name="Intensity Monitor",
        **kwargs
    ):
        super().__init__(ID, name=name, **kwargs)

        self.target = PVEnumAdjustable(ID + ":PROBE_SP", name="target")
        self.target_pos = Motor(ID + ":MOTOR_PROBE", name="target pos")

        self.diodes = DiodeArray(vme_crate, link, ch_up, ch_down, ch_right, ch_left) if vme_crate else None
        self.calib  = Calibrator(ID, calib_channels) if calib_channels else None
        self.calc   = CalcIntensity(calc_channels) if calc_channels else None


    def __repr__(self):
        res = super().__repr__()
        if self.diodes:
            res += "\n" + repr(self.diodes)
        return res



class DiodeArray:

    def __init__(self, vme_crate, link, ch_up, ch_down, ch_right, ch_left):
        prefix = f"{vme_crate}:Lnk{link}Ch"
        self.up    = up    = FeDigitizer(f"{prefix}{ch_up}")
        self.down  = down  = FeDigitizer(f"{prefix}{ch_down}")
        self.left  = left  = FeDigitizer(f"{prefix}{ch_left}")
        self.right = right = FeDigitizer(f"{prefix}{ch_right}")
        self._diodes = dict(up=up, down=down, left=left, right=right)

    def __repr__(self):
        header = format_header("Diode Array", "=")
        res = defaultdict(dict)
        for name, diode in self._diodes.items():
            res["Bias voltage"][name] = diode.bias.get_current_value()
            res["Gain"][name]         = diode.gain.get_current_value()
        res = printable_dict_of_dicts(res, sorter=lambda x: list(x))
        return header + "\n\n" + res

    def get_available_gains(self):
        all_names = set(
            tuple(sorted(diode.gain.states.data.keys())) for diode in self._diodes.values()
        )
        assert len(all_names) == 1, "gain options for the four diodes are not identical"
        return all_names.pop()

    def get_gains(self):
        res = {}
        for diode_name, diode in self._diodes.items():
            gain_name  = diode.gain.get_current_value()
            gain_value = diode.gain.get_current_value(as_number=True)
            res[diode_name] = (gain_name, gain_value)
        return res

    def set_gains(self, value):
        tasks = [diode.gain.set_target_value(value) for diode in self._diodes.values()]
        for t in tasks:
            t.wait()



class Calibrator(Device):

    def __init__(self, ID, channels):
        super().__init__(ID + "-CALIB")

        self.motor_x = mx = Motor(ID + ":MOTOR_X1", name="motor x")
        self.motor_y = my = Motor(ID + ":MOTOR_Y1", name="motor y")
        self._motors = (mx, my)

        signals = {"signal_" + name: PvDataStream(ch) for name, ch in channels.items()}
        self.__dict__.update(signals)
        self._signals = tuple(signals.values())


    def calibrate(self, wait_time=5):
        ci = self.get_calibration_intensity(wait_time=wait_time)
        self.set_calibration_intensity(ci)
        cx, cy = self.get_calibration_position(ci, wait_time=wait_time)
        self.set_calibration_position(cx, cy)
        return ci, cx, cy

    def get_calibration_intensity(self, wait_time=5):
        self._reset_motors()
        return calculate_calibration_intensity(self._signals, wait_time)

    def get_calibration_position(self, calib_intensities, motion_range=0.2, wait_time=5):
        self._set_motor_limits(motion_range)
        self._reset_motors()
        cx = calculate_calibration_position(self.motor_x, self.signal_left, self.signal_right, calib_intensities[:2], motion_range, wait_time)
        cy = calculate_calibration_position(self.motor_y, self.signal_up,   self.signal_down,  calib_intensities[2:], motion_range, wait_time)
        return cx, cy


    def set_calibration_intensity(self, calib_intensities):
        # this list is for bernina when using the SLA ioxos
        chs = [
            "SLAAR21-LTIM01-EVR0:CALCI.INPG",
            "SLAAR21-LTIM01-EVR0:CALCI.INPH",
            "SLAAR21-LTIM01-EVR0:CALCI.INPF",
            "SLAAR21-LTIM01-EVR0:CALCI.INPE",

            "SLAAR21-LTIM01-EVR0:CALCY.INPE",
            "SLAAR21-LTIM01-EVR0:CALCY.INPF",

            "SLAAR21-LTIM01-EVR0:CALCX.INPE",
            "SLAAR21-LTIM01-EVR0:CALCX.INPF"

        ]
        # CALCI gets each norms values, CALCY gets the first two, CALCX gets the last two
        vals = list(calib_intensities) * 2
        fill_channels(chs, vals)


    def set_calibration_position(self, calib_pos_x, calib_pos_y):
        chs = [
            "SLAAR21-LTIM01-EVR0:CALCX.INPJ",
            "SLAAR21-LTIM01-EVR0:CALCX.INPI",

            "SLAAR21-LTIM01-EVR0:CALCY.INPJ",
            "SLAAR21-LTIM01-EVR0:CALCY.INPI"
        ]
        vals = list(calib_pos_x) + list(calib_pos_y)
        fill_channels(chs, vals)


    def _reset_motors(self):
        tasks = [m.set_target_value(0) for m in self._motors]
        for t in tasks:
            t.wait()

    def _set_motor_limits(self, motion_range):
        limit = motion_range / 2 + 0.1
        for m in self._motors:
            m.set_epics_limits(-limit, +limit)



def calculate_calibration_intensity(sigs, wait_time):
    acqs = [d.acquire(seconds=wait_time) for d in sigs]
    data = [a.wait() for a in acqs]
    means = [np.mean(d) for d in data]
#    stds = [np.std(d) for d in data]
    calib = [1 / m / 4 for m in means]
    return calib


def calculate_calibration_position(mot, sig1, sig2, calib_intensities, motion_range, wait_time):
    border = motion_range / 2
    raw = []
    for pos in (-border, +border):
        mot.set_target_value(pos).wait()
        acqs = [s.acquire(seconds=wait_time) for s in (sig1, sig2)]
        v0, v1 = [np.mean(a.wait()) * c for a, c in zip(acqs, calib_intensities)]
        delta  = v0 - v1
        summed = v0 + v1
        res = delta / summed
        raw.append(res)

    grad = motion_range / np.diff(raw)[0]
#    calib = [np.diff(calib_intensities)[0] / np.sum(calib_intensities), grad]
    calib = [0, grad]
    return calib


def fill_channels(chs, vals):
    for c, v in zip(chs, vals):
        PV(c).put(bytes(str(v), "utf8")) #TODO: this is probably not a good idea



class CalcIntensity:

    def __init__(self, channels):
        for name, ch in channels.items():
            ds = PvDataStream(ch)
            setattr(self, name, ds)



