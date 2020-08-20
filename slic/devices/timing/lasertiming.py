import os
from time import sleep, asctime
from types import SimpleNamespace
from abc import ABC, abstractmethod
import numpy as np
from epics import PV

from slic.core.adjustable import Adjustable
from slic.devices.general.motor import check_pos_type
from slic.utils import typename


OSCILLATOR_PERIOD = 1 / 71.368704e6
#POCKELS_CELL_RESOLUTION = 7e-9 #TODO: what was this supposed to do?


class ETiming(Adjustable):

    def __init__(
        self,
        Id,
        pvname_setvalue="SLAAR01-LTIM-PDLY:DELAY",
        pvname_readback="SLAAR-LGEN:DLY_OFFS1",
        pvname_waiting="SLAAR01-LTIM-PDLY:WAITING",
        name="Globi Laser Electronic Timing",
        units="ps"
    ):
        super().__init__(name=name, units=units)
        self.Id = Id

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback,
            waiting  = pvname_waiting
        )

        self.pvs = SimpleNamespace(
            setvalue = PV(pvname_setvalue),
            readback = PV(pvname_readback),
            waiting  = PV(pvname_waiting)
        )


    def get_current_value(self):
        return self.pvs.readback.get() * 1e6 # convert from us to ps

    def set_target_value(self, value, hold=False):
        change = lambda: self.put_and_wait(value)
        return self._as_task(change, hold=hold)

    def put_and_wait(self, value, checktime=0.01):
        self.pvs.setvalue.put(value)
        sleep(0.2)
        while self.is_moving():
            sleep(checktime)

    def is_moving(self):
        waiting = self.pvs.waiting.get()
        return bool(waiting)

    def wait_for_valid_value(self):
        tval = np.nan
        while not np.isfinite(tval):
            tval = self.get_current_value()
        return tval

    def reset_current_value_to(self, value):
        self.pvs.setvalue.put(value)

    def __repr__(self):
        res = super().__repr__()
        setvalue = self.pvs.setvalue.get()
        units = self.units
        res += f" (set value: {setvalue} {units})"
        return res



class LXT(Adjustable):

    def __init__(self, Id_phase_shifter, Id_timing, base_folder, tolerance_poly_coeff=(100e-15, 1e-7), name="Laser X-ray Timing", units="s"):
        super().__init__(name=name, units=units)
        self.Id = Id = Id_phase_shifter #TODO: does that make sense?
        self.tolerance_poly_coeff = tolerance_poly_coeff

        pvname_sdg1_readback = Id_timing + ":Pul2-Delay-RB"
        pvname_sdg1_setvalue = Id_timing + ":Pul2_NEW_DELAY" #TODO: ":Pul2-Delay-SP" ?
        pvname_sdg1_offset   = Id_timing + ":UnivDlyModule1-Delay0-RB"

        pvname_slicer_gate_readback = Id_timing + ":Pul3-Delay-RB"
        pvname_slicer_gate_setvalue = Id_timing + ":Pul3_NEW_DELAY" #TODO: ":Pul3-Delay-SP" ?
        pvname_slicer_gate_offset   = Id_timing + ":UnivDlyModule1-Delay1-RB"

        self.devices = SimpleNamespace(
            phase_shifter = PhaseShifter(Id_phase_shifter, base_folder),
            sdg1 = PockelsTrigger(pvname_sdg1_readback, pvname_sdg1_setvalue, pvname_sdg1_offset, base_folder),
            slicer_gate = PockelsTrigger(pvname_slicer_gate_readback, pvname_slicer_gate_setvalue, pvname_slicer_gate_offset, base_folder)
        )


    def get_current_value(self):
        # pulses are at: INDEX * OSCILLATOR_PERIOD - PHASE_SHIFTER
        # the -PHASE_SHIFTER is due to the inverted sign
        phase_shifter = self.devices.phase_shifter.get()
        sdg1 = self.devices.sdg1.get()
        index = (phase_shifter + sdg1) // OSCILLATOR_PERIOD
        delay = index * OSCILLATOR_PERIOD - phase_shifter
        return -delay

    def set_target_value(self, value, hold=False):
        change = lambda: self.move(value)
        return self._as_task(change, hold=hold)

    def is_moving(self):
        raise NotImplementedError

    def move(self, value, tolerance=None):
        self.devices.sdg1.move(-value)
        self.devices.slicer_gate.move(-value)
        if tolerance is None:
            slope, const = self.tolerance_poly_coeff
            tolerance = np.abs(value) * slope + const
        self.devices.phase_shifter.move(value, tolerance=tolerance)

    def move_sdg1(self, value):
        self.devices.sdg1.move(value)

    def reset_current_value_to(self, value):
        self.devices.phase_shifter.set(value)
        self.devices.sdg1.set(-value)
        self.devices.slicer_gate.set(-value)

    def __repr__(self):
        res = super().__repr__()
        delay = self.get_current_value()
        delay = nice_time_to_str(delay)
        res += f" ({delay})"
        return res



class PhaseShifterAramis(Adjustable):

    def __init__(self, Id, base_folder, name=None):
        super().__init__(name=name)
        self.Id = Id
        self._phase_shifter = PhaseShifter(Id, base_folder)

    def set_target_value(self, value, hold=False):
        change = lambda: self._phase_shifter.move(value)
        return self._as_task(change, hold=hold)

    def get_current_value(self, pos_type="user"):
        check_pos_type(pos_type, {"user", "dial"})
        if pos_type == "user":
            return self._phase_shifter.get()
        if pos_type == "dial":
            return self._phase_shifter.get_dial()

    def is_moving(self):
        raise NotImplementedError

    def reset_current_value_to(self, value, pos_type="user"):
        check_pos_type(pos_type, {"user"})
        if pos_type == "user":
            return self._phase_shifter.set(value)



class OffsetStorageMixin(ABC):

    def __init__(self, base_folder, pvname):
        self.storage = Storage(base_folder, pvname)
        self.filename = self.storage.filename

    @property
    def offset(self):
        return self.storage.value or 0 #TODO: is 0 a sensible default?

    def store(self, value=None):
        if value is None:
            value = self.get_dial()
        self.storage.store(value)

    @abstractmethod
    def get_dial(self):
        raise NotImplementedError



class PhaseShifter(OffsetStorageMixin):

    def __init__(self, pv_basename, base_folder, dial_max=14.0056e-9, tolerance=100e-15):
        self.pv_basename = pv_basename
        self.dial_max = dial_max
        self.tolerance = tolerance

        pvname = pv_basename + ":CURR_DELTA_T" #TODO: should this be the basename only? actually Storage stores the offset!
        super().__init__(base_folder, pvname)

        pvname_setvalue = pv_basename + ":NEW_DELTA_T"
        pvname_readback = pv_basename + ":CURR_DELTA_T"
        pvname_execute  = pv_basename + ":SET_NEW_PHASE.PROC"

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback,
            execute  = pvname_execute
        )

        self.pvs = SimpleNamespace(
            setvalue = PV(pvname_setvalue),
            readback = PV(pvname_readback),
            execute  = PV(pvname_execute)
        )


    def get(self):
        return self.get_dial() - self.offset # offset in s

    def get_dial(self):
        return self.pvs.readback.get() * 1e-12 # convert from ps to s

    def set(self, value):
        new_offset = self.get_dial() - value
        new_offset %= OSCILLATOR_PERIOD
        self.store(new_offset)


    def move(self, value, tolerance=None): # tolerance in s
        dial = value + self.offset
        dial %= OSCILLATOR_PERIOD
        dial = min(dial, self.dial_max)
        dial_ps = dial * 1e12
        self.pvs.setvalue.put(dial_ps)
        sleep(0.1)
        self.pvs.execute.put(1)

        if tolerance is None:
            tolerance = self.tolerance

        while abs(self.get_dial() - dial) > tolerance:
            #print(abs(self.get_dial() - dial), tolerance)
            sleep(0.2)


    def __repr__(self):
        tname = typename(self)
        name = self.pv_basename
        n = 15
        user = time_to_str(self.get(), n=n)
        dial = time_to_str(self.get_dial(), n=n)
        units = "sec"
        return f"{tname} \"{name}\" at {user} {units} (dial at {dial} {units})"



class PockelsTrigger(OffsetStorageMixin):

    def __init__(self, pvname_readback, pvname_setvalue, pvname_offset, base_folder): #TODO make offset optional?
        self.pvname = pvname = pvname_readback
        super().__init__(base_folder, pvname)

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback,
            offset   = pvname_offset
        )

        self.pvs = SimpleNamespace(
            setvalue = PV(pvname_setvalue),
            readback = PV(pvname_readback),
            offset   = PV(pvname_offset)
        )


    def get(self):
        return self.get_dial() - self.offset

    def get_dial(self):
        readback = self.pvs.readback.get() * 1e-6
        readback = round(readback, 9) #TODO: why?
        offset = self.pvs.offset.get() * 1e-9 - 7.41e-9 #TODO what is the constant?
        return readback + offset

    def set(self, value):
        new_offset = self.get_dial() - value
        self.store(new_offset)

    def move(self, value):
        dial = value + self.offset
        self.pvs.setvalue.put(dial * 1e6)

    def __repr__(self):
        tname = typename(self)
        name = self.pvname
        n = 12
        user = time_to_str(self.get(), n=n)
        dial = time_to_str(self.get_dial(), n=n)
        units = "sec"
        return f"{tname} \"{name}\" at {user} {units} (dial at {dial} {units})"



class Storage:
    """
    Read/write a value from/to a file
    """

    def __init__(self, base_folder, filename):
        self.filename = os.path.join(base_folder, filename)
        self.last_value = None
        self.last_read_time = None


    @property
    def value(self):
        if not self.exists:
            fname = self.filename
            print(f"Warning: Storage file \"{fname}\" does not exist") #TODO: raise an error?
            return None

        tlread = self.last_read_time
        tlmod = self.last_modified_time
        if tlread is None or tlmod > tlread:
            self.last_value = self.load()
            self.last_read_time = tlmod

        return self.last_value


    @property
    def exists(self):
        return os.path.isfile(self.filename)

    @property
    def last_modified_time(self):
        if self.exists:
            return os.stat(self.filename).st_mtime

    def store(self, value):
        timestamp = asctime()
        with open(self.filename, "w") as f: #TODO: use numpy here as well?
            f.write(f"# {timestamp}\n")
            f.write(f"{value}\n")

    def load(self):
        value = np.loadtxt(self.filename) #TODO: parse manually here as well?
        return float(value)



def time_to_str(time, n=12):
    fmt = "%%+.%df" % n
    time = fmt % time
    #print(time)
    idx_point = time.find(".")
    ret_str = time[:idx_point] + " ."
    ngroups = (len(time) - idx_point) // 3
    for ng in range(ngroups):
        ret_str += " %s" % time[idx_point + 1 + 3 * ng : idx_point + 1 + 3 * (ng + 1)]
        #print(idx_point + 1 + 3 * ng, idx_point + 1 * 3 * (ng - 1), ret_str)
    return ret_str


def nice_time_to_str(time, fmt="%+.0f"):
    abs_time = abs(time)
    if abs_time >= 1:
        factor = 1
        units = "s"
    elif 1e-3 <= abs_time < 1:
        factor = 1e3
        units = "ms"
    elif 1e-6 <= abs_time < 1e-3:
        factor = 1e6
        units = "us"
    elif 1e-9 <= abs_time < 1e-6:
        factor = 1e9
        units = "ns"
    elif 1e-12 <= abs_time < 1e-9:
        factor = 1e12
        units = "ps"
    elif 1e-15 <= abs_time < 1e-12:
        factor = 1e15
        units = "fs"
    elif 1e-18 <= abs_time < 1e-15:
        factor = 1e18
        units = "as"
    elif abs_time < 1e-18:
        return "0 s"
    else:
        return str(time)
    return fmt % (time * factor) + " " + units



