import subprocess
from types import SimpleNamespace
from contextlib import contextmanager
import colorama

from slic.core.adjustable import Adjustable, AdjustableError
from slic.utils.eco_epics.motor import Motor as EpicsMotor
from slic.utils.eco_epics.utilities_epics import EpicsString
from slic.utils.eco_components.aliases import Alias
from slic.utils.rangebar import RangeBar


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


STATUS_MESSAGES = {
    -13: "invalid value (cannot convert to float). Move not attempted.",
    -12: "target value outside soft limits. Move not attempted.",
    -11: "drive PV is not connected: Move not attempted.",
     -8: "move started, but timed-out.",
     -7: "move started, timed-out, but appears done.",
     -5: "move started, unexpected return value from PV.put()",
     -4: "move-with-wait finished, soft limit violation seen",
     -3: "move-with-wait finished, hard limit violation seen",
      0: "move-with-wait finish OK.",
      0: "move-without-wait executed, not confirmed",
      1: "move-without-wait executed, move confirmed",
      3: "move-without-wait finished, hard limit violation seen",
      4: "move-without-wait finished, soft limit violation seen"
}



class Motor(Adjustable):

    def __init__(self, pvname, name=None):
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

        name = name or pvname
        units = self.pvs.units.value
        super().__init__(name=name, units=units)

        self.status = None
        self.status_message = None


    def get_current_value(self, readback=True, pos_type="user"):
        check_pos_type(pos_type)
        kwargs = POS_TYPE_KWARGS[pos_type]
        return self._motor.get_position(readback=readback, **kwargs)

    def reset_current_value_to(self, value, pos_type="user"):
        check_pos_type(pos_type)
        kwargs = POS_TYPE_KWARGS[pos_type]
        return self._motor.set_position(value, **kwargs)


    def set_target_value(self, value, hold=False, check_limits=True, show_progress=False):
        ignore_limits = not check_limits

        if not show_progress:
            def change():
                self._move(value, ignore_limits=ignore_limits, wait=True)

        else:
            def change():
                start = self.get_current_value()
                stop = value

                with RangeBar(start, stop) as rbar:
                    def on_change(value=None, **kw):
                        rbar.show(value)

                    with self.use_callback(on_change):
                        self._move(stop, ignore_limits=ignore_limits, wait=True)

        return self._as_task(change, hold=hold, stopper=self._motor.stop)


    def _move(self, *args, **kwargs):
        status = self._motor.move(*args, **kwargs)
        message = STATUS_MESSAGES.get(status, f"unknown status code: {status}")
        self.status = status
        self.status_message = message
        validate_status(status, message)


    def is_moving(self):
        done = self.pvs.done_move.value # 0: moving, 1: move done
        return not bool(done)


    def stop(self):
        try:
            return super().stop()
        except:
            self._motor.stop()


    def get_limits(self, pos_type="user"):
        check_pos_type(pos_type)
        ll_name, hl_name = POS_TYPE_LIMIT_NAMES[pos_type]
        low_limit  = self._motor.get(ll_name)
        high_limit = self._motor.get(hl_name)
        return low_limit, high_limit

    def set_limits(self, low_limit, high_limit, relative_to_current=False, pos_type="user"):
        check_pos_type(pos_type)
        ll_name, hl_name = POS_TYPE_LIMIT_NAMES[pos_type]
        if relative_to_current:
            val = self.get_current_value(pos_type=pos_type)
            low_limit  += val
            high_limit += val
        self._motor.put(ll_name, low_limit)
        self._motor.put(hl_name, high_limit)

    def print_limits(self):
        low, high = self.get_limits()
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



def check_pos_type(pos_type):
    if pos_type not in POS_TYPES:
        msg = f"{pos_type} not in {POS_TYPES}"
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



