import time
import subprocess
from types import SimpleNamespace
from enum import IntEnum
from epics import ca

from slic.core.adjustable import Adjustable, AdjustableError
from slic.utils import typename
from slic.utils.printing import printable_dict
from slic.utils.hastyepics import get_pv as PV
from ..basedevice import BaseDevice


class Status(IntEnum):
    STOPPED     = 0
    STEPPING    = 1
    SCANNING    = 2
    HOLDING     = 3
    TARGETING   = 4
    MOVE_DELAY  = 5
    CALIBRATING = 6
    FINDING_REF = 7
    LOCKED      = 8



class SmarActStage(BaseDevice):

    def __init__(self, name=None, **axis_ids):
        self.name = name
        self.axis_ids = axis_ids

        self.axes = {}
        for ax_name, ax_id in axis_ids.items():
            record_name = f"{name}: {ax_name}"
            ax = SmarActAxis(ax_id, name=record_name)
            setattr(self, ax_name, ax)
            self.axes[ax_name] = ax


    def __repr__(self):
        tname = typename(self)
        name = self.name
        head = f"{tname} \"{name}\""

        to_print = {ax_name: ax.get_current_value() for ax_name, ax in self.axes.items()}
        return printable_dict(to_print, head)



class SmarActAxis(Adjustable):

    def __init__(self, ID, name=None, units=None, internal=False):
        super().__init__(ID, name=name, units=units, internal=internal)

        self.wait_time = 0.1
        self.timeout = 60
        self._move_requested = False

        self.pvs = SimpleNamespace(
            drive    = PV(ID + ":DRIVE"),
            readback = PV(ID + ":MOTRBV"),
            hlm      = PV(ID + ":HLM"),
            llm      = PV(ID + ":LLM"),
            status   = PV(ID + ":STATUS"),
            set_pos  = PV(ID + ":SET_POS"),
            stop     = PV(ID + ":STOP.PROC"),
            hold     = PV(ID + ":HOLD"),
            twv      = PV(ID + ":TWV"),
            units    = PV(ID + ":DRIVE.EGU")
        )


    @property
    def units(self):
        units = self._units
        if units is not None:
            return units
        return self.pvs.units.get()

    @units.setter
    def units(self, value):
        self._units = value


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.drive.get()

    def reset_current_value_to(self, value):
        return self.pvs.set_pos.put(value)

    def set_target_value(self, value):
        wait_time = self.wait_time
        timeout = self.timeout + time.time()

        self._move_requested = True
        self.pvs.drive.put(value, wait=True)

        # wait for start
        while self._move_requested and not self.is_moving():
            time.sleep(wait_time)
            if time.time() >= timeout:
                tname = typename(self)
                self.stop()
                raise SmarActError(f"starting to move {tname} \"{self.name}\" to {value} {self.units} timed out")

        # wait for move done
        while self._move_requested and self.is_moving():
            if self.is_holding(): # holding == arrived at target!
                break
            time.sleep(wait_time)

        self._move_requested = False


    def stop(self):
        self._move_requested = False
        self.pvs.stop.put(1, wait=True)


    def is_moving(self):
        return self.status != Status.STOPPED

    def is_holding(self):
        return self.status == Status.HOLDING

    @property
    def status(self):
        return self.pvs.status.get()


    def within_epics_limits(self, val):
        low, high = self.get_epics_limits()
        return low <= val <= high

    def get_epics_limits(self):
        low  = self.pvs.llm.get()
        high = self.pvs.hlm.get()
        return low, high

    def set_epics_limits(self, low, high, relative_to_current=False):
        low  = -np.inf if low  is None else low
        high = +np.inf if high is None else high
        if relative_to_current:
            val = self.get_current_value()
            low  += val
            high += val
        self.pvs.llm.put(low)
        self.pvs.hlm.put(high)


    def move(self, val, relative=False, wait=False, ignore_limits=False, confirm_move=False, timeout=300.0):
        """
        moves SmarAct drive to position (emulating pyepics Motor class)

        arguments:
        ==========
         val            value to move to (float) [Must be provided]
         relative       move relative to current position    (T/F) [F]
         wait           whether to wait for move to complete (T/F) [F]
         ignore_limits  try move without regard to limits    (T/F) [F]
         confirm_move   try to confirm that move has begun   (T/F) [F]
         timeout        max time for move to complete (in seconds) [300]

        return values:
        ==============
         -13 : invalid value (cannot convert to float).  Move not attempted.
         -12 : target value outside soft limits.         Move not attempted.
         -11 : drive PV is not connected.                Move not attempted.
          -8 : move started, but timed-out.
        # -7 : move started, timed-out, but appears done.
          -5 : move started, unexpected return value from PV.put().
        # -4 : move-with-wait finished, soft limit violation seen.
        # -3 : move-with-wait finished, hard limit violation seen.
           0 : move-with-wait finished OK.
           0 : move-without-wait executed, move not confirmed.
           1 : move-without-wait executed, move confirmed.
        #  3 : move-without-wait finished, hard limit violation seen.
        #  4 : move-without-wait finished, soft limit violation seen.

        """
        INVALID_VALUE  = -13
        OUTSIDE_LIMITS = -12
        NOT_CONNECTED  = -11
        TIMEOUT        =  -8
        UNKNOWN_ERROR  =  -5
        SUCCESS        =   0
        EXECUTED       =   0
        CONFIRMED      =   1

        PUT_SUCCESS    =   1
        PUT_TIMEOUT    =  -1

        try:
            val = float(val)
        except Exception:
            return INVALID_VALUE

        if relative:
            val += self.pvs.drive.get()

        if not ignore_limits:
            if not self.within_epics_limits(val):
                return OUTSIDE_LIMITS

        put_stat = self.pvs.drive.put(val, wait=wait, timeout=timeout)

        if put_stat is None:
            return NOT_CONNECTED

        if wait and put_stat == PUT_TIMEOUT:
            return TIMEOUT

        if put_stat != PUT_SUCCESS:
            return UNKNOWN_ERROR

        stat = self.status

        t0 = time.time()
        thold  = t0 + self.pvs.hold.get() * 0.001
        tstart = t0 + min(timeout, 10)
        tout   = t0 + timeout

        if not wait and not confirm_move:
            return EXECUTED

        while stat == Status.HOLDING and time.time() <= thold:
            ca.poll(evt=1.0e-2)
            stat = self.status

        while stat == Status.STOPPED and time.time() <= tstart:
            ca.poll(evt=1.0e-2)
            stat = self.status

        if stat != Status.TARGETING:
            if time.time() > tout:
                return TIMEOUT
            else:
                return UNKNOWN_ERROR

        if not wait:
            return CONFIRMED

        while stat == Status.TARGETING and time.time() <= tout:
            ca.poll(evt=1.0e-2)
            stat = self.status

        if stat not in (Status.HOLDING, Status.TARGETING):
            return UNKNOWN_ERROR

        if time.time() > tout:
            return TIMEOUT

        twv = self.pvs.twv.get()
        twv = abs(twv)

        while stat == Status.HOLDING and time.time() <= tout:
            ca.poll(evt=1.0e-2)
            stat = self.status

            delta = self.pvs.readback.get() - val
            delta = abs(delta)
            if delta < twv:
                return SUCCESS

        return UNKNOWN_ERROR


    def gui(self):
        device, motor = self.ID.split(":")
        cmd = f'caqtdm -macro "P={device}:,M={motor}" ESB_MX_SMARACT_mot_exp.ui'
        return subprocess.Popen(cmd, shell=True)



class SmarActError(AdjustableError):
    pass



