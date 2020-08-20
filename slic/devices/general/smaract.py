import time
import subprocess
from types import SimpleNamespace
from epics import PV, ca

from slic.core.adjustable import Adjustable, AdjustableError
from slic.utils import typename
from slic.utils.printing import printable_dict
from ..basedevice import BaseDevice


class SmarActStage(BaseDevice):

    def __init__(self, name=None, **axis_ids):
        self.name = name
        self.axis_ids = axis_ids

        self.axes = {}
        for ax_name, ax_id in axis_ids.items():
            record_name = f"{name}: {ax_name}"
            ax = SmarActRecord(ax_id, name=record_name)
            setattr(self, ax_name, ax)
            self.axes[ax_name] = ax


    def __repr__(self):
        tname = typename(self)
        name = self.name
        head = f"{tname} \"{name}\""

        to_print = {ax_name: ax.get_current_value() for ax_name, ax in self.axes.items()}
        return printable_dict(to_print, head)



class SmarActRecord(Adjustable):

    def __init__(self, Id, name=None):
        units = PV(Id + ":DRIVE.EGU").get() #TODO
        super().__init__(name=name, units=units)
        self.Id = Id

        self.pvs = SimpleNamespace(
            drive    = PV(Id + ":DRIVE"),
            readback = PV(Id + ":MOTRBV"),
            hlm      = PV(Id + ":HLM"),
            llm      = PV(Id + ":LLM"),
            status   = PV(Id + ":STATUS"),
            set_pos  = PV(Id + ":SET_POS"),
            stop     = PV(Id + ":STOP.PROC"),
            hold     = PV(Id + ":HOLD"),
            twv      = PV(Id + ":TWV")
        )


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.drive.get()

    def reset_current_value_to(self, value):
        return self.pvs.set_pos.put(value)

    def set_target_value(self, value, hold=False):
        change  = lambda: self._move(value)
        stopper = lambda: self.pvs.stop.put(1)
        return self._as_task(change, stopper=stopper, hold=hold)

    def _move(self, value, checktime=0.1):
        self.pvs.drive.put(value)
        while self.is_moving():
            time.sleep(checktime)

    def is_moving(self):
        return self.pvs.status.get() != 0

    def stop(self):
        try:
            return super().stop()
        except:
            self.pvs.stop.put(1)


    def within_limits(self, val):
        low, high = self.get_limits()
        return low <= val <= high

    def get_limits(self):
        low  = self.pvs.llm.get()
        high = self.pvs.hlm.get()
        return low, high

    def set_limits(self, low, high, relative_to_current=False):
        if relative_to_current:
            val = self.get_current_value()
            low  += val
            high += val
        self.pvs.llm.put(low)
        self.pvs.hlm.put(high)


    def move(self, val, relative=False, wait=False, timeout=300.0, ignore_limits=False, confirm_move=False):
        """ moves smaract drive to position (emulating pyepics Motor class)

        arguments:
        ==========
         val            value to move to (float) [Must be provided]
         relative       move relative to current position    (T/F) [F]
         wait           whether to wait for move to complete (T/F) [F]
         ignore_limits  try move without regard to limits    (T/F) [F]
         confirm_move   try to confirm that move has begun   (T/F) [F]
         timeout        max time for move to complete (in seconds) [300]

        return values:
          -13 : invalid value (cannot convert to float).  Move not attempted.
          -12 : target value outside soft limits.         Move not attempted.
          -11 : drive PV is not connected:                Move not attempted.
           -8 : move started, but timed-out.
           -7 : move started, timed-out, but appears done.
           -5 : move started, unexpected return value from PV.put()
           -4 : move-with-wait finished, soft limit violation seen
           -3 : move-with-wait finished, hard limit violation seen
            0 : move-with-wait finish OK.
            0 : move-without-wait executed, not confirmed
            1 : move-without-wait executed, move confirmed 
            3 : move-without-wait finished, hard limit violation seen
            4 : move-without-wait finished, soft limit violation seen

        """
        NONFLOAT, OUTSIDE_LIMITS, UNCONNECTED = -13, -12, -11
        TIMEOUT = -8
        UNKNOWN_ERROR = -5
        DONE_OK = 0
        MOVE_BEGUN, MOVE_BEGUN_CONFIRMED = 0, 1
        try:
            val = float(val)
        except TypeError:
            return NONFLOAT

        if relative:
            val += self.pvs.drive.get()

        # Check for limit violations
        if not ignore_limits:
            if not self.within_limits(val):
                return OUTSIDE_LIMITS

        stat = self.pvs.drive.put(val, wait=wait, timeout=timeout)
        if stat is None:
            return UNCONNECTED

        if wait and stat == -1:
            return TIMEOUT

        if 1 == stat:
            s0 = self.pvs.status.get()
            s1 = s0
            t0 = time.time()
            t1 = t0 + min(10.0, timeout)  # should be moving by now
            thold = self.pvs.hold.get() * 0.001 + t0
            tout = t0 + timeout
            if wait or confirm_move:
                while time.time() <= thold and s1 == 3:
                    ca.poll(evt=1.0e-2)
                    s1 = self.pvs.status.get()
                while time.time() <= t1 and s1 == 0:
                    ca.poll(evt=1.0e-2)
                    s1 = self.pvs.status.get()
                if s1 == 4:
                    if wait:
                        while time.time() <= tout and s1 == 4:
                            ca.poll(evt=1.0e-2)
                            s1 = self.pvs.status.get()
                        if s1 == 3 or s1 == 4:
                            if time.time() > tout:
                                return TIMEOUT
                            else:
                                twv = abs(self.pvs.twv.get())
                                while s1 == 3 and time.time() <= tout and abs(self.pvs.readback.get() - val) >= twv:
                                    ca.poll(evt=1.0e-2)
                                return DONE_OK
                    else:
                        return MOVE_BEGUN_CONFIRMED
                elif time.time() > tout:
                    return TIMEOUT
                else:
                    return UNKNOWN_ERROR
            else:
                return MOVE_BEGUN
        return UNKNOWN_ERROR


    def gui(self):
        device, motor = self.Id.split(":")
        cmd = f'caqtdm -macro "P={device}:,M={motor}" ESB_MX_SMARACT_mot_exp.ui'
        return subprocess.Popen(cmd, shell=True)



class SmarActError(AdjustableError):
    pass



