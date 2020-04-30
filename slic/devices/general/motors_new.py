from slic.controls.eco_epics.motor import Motor as _Motor
from slic.controls.eco_epics.utilities_epics import EpicsString
import subprocess
from epics import PV
from slic.task import Changer
from slic.utils.eco_components.aliases import Alias
from .adjustable import spec_convenience, ValueInRange, update_changes, AdjustableError
import colorama

_MotorRocordStandardProperties = {}
_posTypes = ["user", "dial", "raw"]
_guiTypes = ["xdm"]


_status_messages = {
    -13: "invalid value (cannot convert to float).  Move not attempted.",
    -12: "target value outside soft limits.         Move not attempted.",
    -11: "drive PV is not connected:                Move not attempted.",
    -8: "move started, but timed-out.",
    -7: "move started, timed-out, but appears done.",
    -5: "move started, unexpected return value from PV.put()",
    -4: "move-with-wait finished, soft limit violation seen",
    -3: "move-with-wait finished, hard limit violation seen",
    0: "move-with-wait finish OK.",
    1: "move-without-wait executed, not confirmed",
    2: "move-without-wait executed, move confirmed",
    3: "move-without-wait finished, hard limit violation seen",
    4: "move-without-wait finished, soft limit violation seen",
}


def _keywordChecker(kw_key_list_tups):
    for tkw, tkey, tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s" % (tkw, tlist)


@spec_convenience
@update_changes
class MotorRecord:
    def __init__(
        self,
        pvname,
        name=None,
        elog=None,
        alias_fields={"readback": "RBV", "user_offset": "OFF"},
    ):
        self.Id = pvname
        self._motor = _Motor(pvname)
        self._elog = elog
        self.name = name
        self.alias = Alias(name)
        for an, af in alias_fields.items():
            self.alias.append(
                Alias(an, channel=".".join([pvname, af]), channeltype="CA")
            )
        self._currentChange = None
        self.description = EpicsString(pvname+'.DESC')

    # Conventional methods and properties for all Adjustable objects
    def set_target_value(self, value, hold=False, check=True):
        """ Adjustable convention"""

        def changer(value):
            self._status = self._motor.move(value, ignore_limits=(not check), wait=True)
            self._status_message = _status_messages[self._status]
            if self._status < 0:
                raise AdjustableError(self._status_message)
            elif self._status > 0:
                print("\n")
                print(self._status_message)

        #        changer = lambda value: self._motor.move(\
        #                value, ignore_limits=(not check),
        #                wait=True)
        return Changer(
            target=value,
            parent=self,
            changer=changer,
            hold=hold,
            stopper=self._motor.stop,
        )

    def stop(self):
        """ Adjustable convention"""
        try:
            self._currentChange.stop()
        except:
            self._motor.stop()
        pass

    def get_current_value(self, posType="user", readback=True):
        """ Adjustable convention"""
        _keywordChecker([("posType", posType, _posTypes)])
        if posType == "user":
            return self._motor.get_position(readback=readback)
        if posType == "dial":
            return self._motor.get_position(readback=readback, dial=True)
        if posType == "raw":
            return self._motor.get_position(readback=readback, raw=True)

    def reset_current_value_to(self, value, posType="user"):
        """ Adjustable convention"""
        _keywordChecker([("posType", posType, _posTypes)])
        if posType == "user":
            return self._motor.set_position(value)
        if posType == "dial":
            return self._motor.set_position(value, dial=True)
        if posType == "raw":
            return self._motor.set_position(value, raw=True)

    def get_precision(self):
        """ Adjustable convention"""
        pass

    def set_precision(self):
        """ Adjustable convention"""
        pass

    precision = property(get_precision, set_precision)

    def set_speed(self):
        """ Adjustable convention"""
        pass

    def get_speed(self):
        """ Adjustable convention"""
        pass

    def set_speedMax(self):
        """ Adjustable convention"""
        pass

    def get_moveDone(self):
        """ Adjustable convention"""
        """ 0: moving 1: move done"""
        return PV(str(self.Id + ".DMOV")).value

    def set_limits(
        self, low_limit, high_limit, posType="user", relative_to_present=False
    ):
        """ 
        set limits. usage: set_limits(low_limit, high_limit)
        
        """
        _keywordChecker([("posType", posType, _posTypes)])
        ll_name, hl_name = "LLM", "HLM"
        if posType is "dial":
            ll_name, hl_name = "DLLM", "DHLM"
        if relative_to_present:
            v = self.get_current_value(posType=posType)
            low_limit = v + low_limit
            high_limit = v + high_limit
        self._motor.put(ll_name, low_limit)
        self._motor.put(hl_name, high_limit)

    def add_value_callback(self, callback, index=None):
        return self._motor.get_pv("RBV").add_callback(callback=callback, index=index)

    def clear_value_callback(self, index=None):
        if index:
            self._motor.get_pv("RBV").remove_callback(index)
        else:
            self._motor.get_pv("RBV").clear_callbacks()

    def get_limits(self, posType="user"):
        """ Adjustable convention"""
        _keywordChecker([("posType", posType, _posTypes)])
        ll_name, hl_name = "LLM", "HLM"
        if posType is "dial":
            ll_name, hl_name = "DLLM", "DHLM"
        return self._motor.get(ll_name), self._motor.get(hl_name)

    def gui(self, guiType="xdm"):
        """ Adjustable convention"""
        cmd = ["caqtdm", "-macro"]

        cmd.append('"P=%s:,M=%s"' % tuple(self.Id.split(":")))
        # cmd.append('/sf/common/config/qt/motorx_more.ui')
        cmd.append("motorx_more.ui")
        # os.system(' '.join(cmd))
        return subprocess.Popen(" ".join(cmd), shell=True)

    # return string with motor value as variable representation
    def __str__(self):
        # """ return short info for the current motor"""
        s = f"{self.name}"
        s += f"\t@ {colorama.Style.BRIGHT}{self.get_current_value():1.6g}{colorama.Style.RESET_ALL} (dial @ {self.get_current_value(posType='dial'):1.6g})"
        # # s +=  "\tuser limits      (low,high) : {:1.6g},{:1.6g}\n".format(*self.get_limits())
        s += f"\n{colorama.Style.DIM}low limit {colorama.Style.RESET_ALL}"
        s += ValueInRange(*self.get_limits()).get_str(self.get_current_value())
        s += f" {colorama.Style.DIM}high limit{colorama.Style.RESET_ALL}"
        # # s +=  "\tuser limits      (low,high) : {:1.6g},{1.6g}".format(self.get_limits())
        return s

    def __repr__(self):
        print(str(self))
        return object.__repr__(self)

    def __call__(self, value):
        self._currentChange = self.set_target_value(value)



