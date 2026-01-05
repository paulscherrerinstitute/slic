import subprocess
from types import SimpleNamespace
from contextlib import contextmanager
import numpy as np

from slic.core.adjustable import Adjustable, AdjustableError
from slic.core.adjustable.convenience import SpecConvenienceProgress
from slic.utils.rangebar import RangeBar
from slic.utils.hastyepics import Motor as EpicsMotor


POS_TYPES = {"dial", "raw", "user"}

POS_TYPE_KWARGS = {
    "dial": {"dial": True},
    "raw":  {"raw":  True},
    "user": {}
}

POS_TYPE_LIMIT_NAMES = {
    "dial": ("DLLM", "DHLM"),
    "raw":  ("LLM",  "HLM"),
    "user": ("LLM",  "HLM")
}


# https://pyepics.github.io/pyepics/devices.html#motor.move
STATUS_MESSAGES = {
    -13: "move not attempted: invalid target value (cannot convert to float)",
    -12: "move not attempted: target value outside soft limits",
    -11: "move not attempted: drive PV not connected",
     -8: "move started, but timed out",
     -7: "move started, timed out, but appears done",
     -5: "move started, but PV.put() returned unexpected value",
     -4: "move with wait finished, but soft limit violation seen",
     -3: "move with wait finished, but hard limit violation seen",
   1000: "move with wait finished OK", # this is also 0 in pyepics
      0: "move without wait executed, start not confirmed",
      1: "move without wait executed, start confirmed",
      3: "move without wait finished, but hard limit violation seen",
      4: "move without wait finished, but soft limit violation seen"
}



class Motor(Adjustable, SpecConvenienceProgress):

    def __init__(self, pvname, ID=None, name=None, units=None, internal=False):
        self.pvname = pvname
        self._motor = motor = EpicsMotor(pvname)

        self.pvs = SimpleNamespace(
            readback    = motor.get_pv("RBV"),
            direction   = motor.get_pv("DIR"),
            offset      = motor.get_pv("OFF"),
            done_move   = motor.get_pv("DMOV"),
            description = motor.get_pv("DESC"),
            units       = motor.get_pv("EGU")
        )

        ID = ID or pvname
        super().__init__(ID, name=name, units=units, internal=internal)

        self.status = None
        self.status_message = None


    @property
    def units(self):
        units = self._units
        if units is not None:
            return units
        return self.pvs.units.value

    @units.setter
    def units(self, value):
        self._units = value


    def get_current_value(self, readback=True, pos_type="user"):
        check_pos_type(pos_type)
        kwargs = POS_TYPE_KWARGS[pos_type]
        return self._motor.get_position(readback=readback, **kwargs)

    def reset_current_value_to(self, value, pos_type="user"):
        check_pos_type(pos_type)
        kwargs = POS_TYPE_KWARGS[pos_type]
        return self._motor.set_position(value, **kwargs)


    def set_target_value(self, value, check_limits=True, show_progress=False):
        ignore_limits = not check_limits

        low, high = self.get_epics_limits()
        if low == high == 0:
            ignore_limits = True

        if not show_progress:
            self._move(value, ignore_limits=ignore_limits)

        else:
            start = self.get_current_value()
            stop = value

            with RangeBar(start, stop) as rbar:
                def on_change(value=None, **kw):
                    rbar.show(value)

                with self.use_callback(on_change):
                    self._move(stop, ignore_limits=ignore_limits)


    def _move(self, *args, wait=True, **kwargs):
        status = self._motor.move(*args, wait=wait, **kwargs)
        if status == 0 and wait:
            status = 1000
        message = STATUS_MESSAGES.get(status, f"unknown status code: {status}")
        self.status = status
        self.status_message = message
        validate_status(status, message)


    def is_moving(self):
        done = self.pvs.done_move.value # 0: moving, 1: move done
        return not bool(done)


    def stop(self):
        self._motor.stop()


    def get_epics_limits(self, pos_type="user"):
        check_pos_type(pos_type)
        low_name, high_name = POS_TYPE_LIMIT_NAMES[pos_type]
        low  = self._motor.get(low_name)
        high = self._motor.get(high_name)
        return low, high

    def set_epics_limits(self, low, high, relative_to_current=False, pos_type="user"):
        check_pos_type(pos_type)
        low_name, high_name = POS_TYPE_LIMIT_NAMES[pos_type]
        if low is None and high is None:
            low = high = 0
            self._motor.put(low_name, low)
            self._motor.put(high_name, high)
            return
        if low  is None: low  = -np.inf
        if high is None: high = +np.inf
        if relative_to_current:
            val = self.get_current_value(pos_type=pos_type)
            low  += val
            high += val
        self._motor.put(low_name, low)
        self._motor.put(high_name, high)

    def print_epics_limits(self):
        low, high = self.get_epics_limits()
        val = self.get_current_value()
        res = RangeBar(low, high).get(val)
        print(res)


    def add_callback(self, callback, index=None):
        return self.pvs.readback.add_callback(callback=callback, index=index)

    def remove_callback(self, index=None):
        if index is not None:
            self.pvs.readback.remove_callback(index)
        else:
            self.pvs.readback.clear_callbacks()

    @contextmanager
    def use_callback(self, callback):
        index = self.add_callback(callback)
        try:
            yield index
        finally:
            self.remove_callback(index)


    def gui(self):
        device, motor = self.pvname.split(":")
        cmd = f'caqtdm -macro "P={device}:,M={motor}" motorx_more.ui'
        return subprocess.Popen(cmd, shell=True)

    @property
    def description(self):
        return self.pvs.description.value

    def print_dial(self):
        dial = self.get_current_value(pos_type="dial")
        offset = self.pvs.offset.value
        direction = self.pvs.direction.value
        res = f"dial at {dial} (direction={direction}, offset={offset})"
        print(res)



def check_pos_type(pos_type, allowed=POS_TYPES):
    if pos_type not in allowed:
        msg = f"pos type \"{pos_type}\" not in {allowed}"
        raise ValueError(msg)


def validate_status(status, message):
    if status < 0:
        raise MotorError(message)
    elif status > 0:
        print()
        print(message)


class MotorError(AdjustableError):
    pass



#TODO
#- precision
#- speed
#- speedMax



