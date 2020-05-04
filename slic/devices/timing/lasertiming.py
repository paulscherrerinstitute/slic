from epics import PV
import os
import numpy as np
import time
from slic.core.task import Task


_basefolder = "/sf/bernina/config/eco/offsets"


def timeToStr(value, n=12):
    fmt = "%%+.%df" % n
    value = fmt % value
    # print(value)
    idx_point = value.find(".")
    ret_str = value[:idx_point] + " ."
    ngroups = (len(value) - idx_point) // 3
    for n in range(ngroups):
        ret_str += " %s" % value[idx_point + 1 + 3 * n : idx_point + 1 + 3 * (n + 1)]
        # print(idx_point+1+3*n,idx_point+1*3*(n-1),ret_str)
    return ret_str


def niceTimeToStr(delay, fmt="%+.0f"):
    a_delay = abs(delay)
    if a_delay >= 1:
        ret = fmt % delay + "s"
    elif 1e-3 <= a_delay < 1:
        ret = fmt % (delay * 1e3) + "ms"
    elif 1e-6 <= a_delay < 1e-3:
        ret = fmt % (delay * 1e6) + "us"
    elif 1e-9 <= a_delay < 1e-6:
        ret = fmt % (delay * 1e9) + "ns"
    elif 1e-12 <= a_delay < 1e-9:
        ret = fmt % (delay * 1e12) + "ps"
    elif 1e-15 <= a_delay < 1e-12:
        ret = fmt % (delay * 1e12) + "fs"
    elif 1e-18 <= a_delay < 1e-15:
        ret = fmt % (delay * 1e12) + "as"
    elif a_delay < 1e-18:
        ret = "0s"
    else:
        ret = str(delay) + "s"
    return ret


class Storage(object):
    """ this class is needed to store the offset in files and read in s """

    def __init__(self, pvname):
        self._filename = os.path.join(_basefolder, pvname)
        self.pvname = pvname
        self.last_read_time = -1

    @property
    def last_modified_time(self):
        if os.path.isfile(self._filename):
            return os.stat(self._filename).st_mtime
        else:
            return -1

    @property
    def value(self):
        lmod = self.last_modified_time
        if os.path.isfile(self._filename):
            # need to read again ?
            if self.last_read_time == -1 or lmod > self.last_read_time:
                # print("actually reading")
                value = float(np.loadtxt(self._filename))
                self.last_read_time = lmod
                self.last_read = value
            else:
                value = self.last_read
        else:
            print("could not read", self._filename)
            value = 0
        return value

    def store(self, value):
        with open(self._filename, "w") as f:
            f.write("# %s\n" % time.asctime())
            f.write("%.15f" % value)


class Pockels_trigger(PV):
    def __init__(self, pv_get, pv_set, pv_offset_get=None):
        pvname = pv_get
        PV.__init__(self, pvname)
        self._pv_offset_get = PV(pv_offset_get)
        self._pv_setvalue = PV(pv_set)
        self._filename = os.path.join(_basefolder, pvname)
        self._storage = Storage(pvname)

    @property
    def offset(self):
        return self._storage.value

    def get_dial(self):
        return (
            np.round(super().get() * 1e-6, 9)
            + self._pv_offset_get.get() * 1e-9
            - 7.41e-9
        )

    def get(self):
        """ convert time to sec """
        return self.get_dial() - self.offset

    def store(self, value=None):
        if value == None:
            value = self.get_dial()
        self._storage.store(value)

    def move(self, value):
        dial = value + self.offset
        self._pv_setvalue.put(dial * 1e6)

    def set(self, value):
        newoffset = self.get_dial() - value
        self.store(newoffset)

    def __repr__(self):
        dial = timeToStr(self.get_dial(), n=12)
        user = timeToStr(self.get(), n=12)
        return "Pockel Trigger PV: %s user , dial = %s, %s" % (self.pvname, user, dial)


_OSCILLATOR_PERIOD = 1 / 71.368704e6


class Phase_shifter(PV):
    """ this class is needed to store the offset in files and read in ps """

    def __init__(
        self, pv_basename="SLAAR02-TSPL-EPL", dial_max=14.0056e-9, precision=100e-15
    ):
        pvname = pv_basename + ":CURR_DELTA_T"
        PV.__init__(self, pvname)
        self._filename = os.path.join(_basefolder, pvname)
        self._pv_setvalue = PV(pv_basename + ":NEW_DELTA_T")
        self._pv_execute = PV(pv_basename + ":SET_NEW_PHASE.PROC")
        self._storage = Storage(pvname)
        self.dial_max = dial_max
        self.retry = precision

    @property
    def offset(self):
        return self._storage.value

    def get_dial(self):
        return super().get() * 1e-12

    def get(self):
        """ convert time to sec """
        return self.get_dial() - self.offset

    def store(self, value=None):
        if value == None:
            value = self.get_dial()
        self._storage.store(value)

    def move(self, value, accuracy=None):
        if accuracy is None:
            accuracy = self.retry
        dial = value + self.offset
        dial = np.mod(dial, _OSCILLATOR_PERIOD)
        if dial > self.dial_max:
            dial = self.dial_max
        dial_ps = dial * 1e12
        self._pv_setvalue.put(dial_ps)
        time.sleep(0.1)
        self._pv_execute.put(1)
        # print(accuracy)
        while np.abs(self.get_dial() - dial) > accuracy:
            # print(np.abs(self.get_dial()-dial))
            time.sleep(0.2)

    def set(self, value):
        newoffset = self.get_dial() - value
        newoffset = np.mod(newoffset, _OSCILLATOR_PERIOD)
        self.store(newoffset)

    def __repr__(self):
        dial = timeToStr(self.get_dial(), n=15)
        user = timeToStr(self.get(), n=15)
        return "Phase Shifter: user,dial = %s , %s" % (user, dial)


_slicer_gate = Pockels_trigger(
    "SLAAR-LTIM02-EVR0:Pul3-Delay-RB",
    "SLAAR-LTIM02-EVR0:Pul3_NEW_DELAY",
    pv_offset_get="SLAAR-LTIM02-EVR0:UnivDlyModule1-Delay1-RB",
)

_sdg1 = Pockels_trigger(
    "SLAAR-LTIM02-EVR0:Pul2-Delay-RB",
    "SLAAR-LTIM02-EVR0:Pul2_NEW_DELAY",
    pv_offset_get="SLAAR-LTIM02-EVR0:UnivDlyModule1-Delay0-RB",
)

_phase_shifter = Phase_shifter("SLAAR02-TSPL-EPL")


_POCKELS_CELL_RESOLUTION = 7e-9


class Lxt(object):
    def __init__(self, accuracy_poly=[100e-15, 1e-7]):
        self.sdg1 = _sdg1
        self.slicer_gate = _slicer_gate
        self.phase_shifter = _phase_shifter
        self.Id = "SLAAR02-TSPL-EPL"
        self.name = "lxt"
        self.elog = None
        self.accuracy_poly = accuracy_poly

    def move_sdg(self, value):
        self.sdg1.move(value)

    def move(self, value, accuracy=None):
        self.sdg1.move(-value)
        self.slicer_gate.move(-value)
        if not accuracy:
            accuracy = np.abs(value) * self.accuracy_poly[1] + self.accuracy_poly[0]
        self.phase_shifter.move(value, accuracy=accuracy)

    def set(self, value):
        self.phase_shifter.set(value)
        self.slicer_gate.set(-value)
        self.sdg1.set(-value)

    def get(self):
        # pulses are at SOME_IDX*OSCILLATOR_PERIOD-PHASESHITER
        # the -PHASESHITER is due to the inverted sign
        phase_shifter = self.phase_shifter.get()
        sdg1_delay = self.sdg1.get()

        idx_pulse = (sdg1_delay + phase_shifter) / _OSCILLATOR_PERIOD

        delay = int(idx_pulse) * _OSCILLATOR_PERIOD - phase_shifter
        return -delay

    def set_target_value(self, value, hold=False):
        """ Adjustable convention"""
        changer = lambda: self.move(value)
        return Task(changer, hold=hold)

    def get_current_value(self):
        return self.get()

    def set_current_value(self, value):
        self.set(value)

    def __repr__(self):
        delay = niceTimeToStr(lxt.get())
        return "delay = %s" % (delay)


lxt = Lxt()
