from epics import PV
import os
import numpy as np
import time
from slic.core.task import Task

_basefolder = "/sf/alvra/config/lasertiming"
_posTypes = ["user", "dial", "raw"]


def timeToStr(value, n=12):
    fmt = "%%+.%df" % n
    value = fmt % value
    #print(value)
    idx_point = value.find(".")
    ret_str = value[:idx_point] + " ."
    ngroups = (len(value) - idx_point) // 3
    for n in range(ngroups):
        ret_str += " %s" % value[idx_point + 1 + 3 * n : idx_point + 1 + 3 * (n + 1)]
        #print(idx_point+1+3*n,idx_point+1*3*(n-1),ret_str)
    return ret_str


class Storage(object):

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
                #print("actually reading")
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

    """ this class is needed to store the offset in files and read in s """

    def __init__(self, pv_basename):
        pvname = pv_basename + "-RB"
        PV.__init__(self, pvname)
        self._pv_setvalue = PV(pv_basename + "-SP")
        self._filename = os.path.join(_basefolder, pvname)
        self._storage = Storage(pvname)

    @property
    def offset(self):
        return self._storage.value

    def get_dial(self):
        return super().get() * 1e-6

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


class Phase_shifter(PV):
    """ this class is needed to store the offset in files and read in ps """

    def __init__(self, pv_basename="SLAAR01-TSPL-EPL"):
        pvname = pv_basename + ":CURR_DELTA_T"
        PV.__init__(self, pvname)
        self._filename = os.path.join(_basefolder, pvname)
        self._pv_setvalue = PV(pv_basename + ":NEW_DELTA_T")
        self._pv_execute = PV(pv_basename + ":SET_NEW_PHASE.PROC")
        self._storage = Storage(pvname)

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

    def move(self, value):
        dial = value + self.offset
        dial_ps = dial * 1e12
        self._pv_setvalue.put(dial_ps)
        time.sleep(0.1)
        self._pv_execute.put(1)
        while np.abs(self.get() - value) > 100e-15:
            time.sleep(0.2)

    def set(self, value):
        newoffset = self.get_dial() - value
        self.store(newoffset)

    def __repr__(self):
        dial = timeToStr(self.get_dial(), n=15)
        user = timeToStr(self.get(), n=15)
        return "Phase Shifter: user,dial = %s , %s" % (user, dial)


#_pockels_in  = Pockels_trigger("SLAAR-LTIM01-EVR0:Pul2-Delay")
#_pockels_out = Pockels_trigger("SLAAR-LTIM01-EVR0:Pul3-Delay")
#_phase_shifter = Phase_shifter("SLAAR01-TSPL-EPL")


class PhaseShifterAramis:

    def __init__(self, Id, name=None, elog=None, z_undulator=None, description=None):
        self.Id = Id
        self._pshifter = Phase_shifter(Id)
        self._elog = elog
        self.name = name

    def set_target_value(self, value, hold=False, check=True):
        """ Adjustable convention"""
        mover = lambda: self._pshifter.move(value)
        return Task(mover, hold=hold)

    def stop(self):
        """ Adjustable convention"""
        pass

    def get_current_value(self, posType="user", readback=True):
        """ Adjustable convention"""
        _keywordChecker([("posType", posType, _posTypes)])
        if posType == "user":
            return self._pshifter.get()
        if posType == "dial":
            return self._pshifter.get_dial()

    def set_current_value(self, value, posType="user"):
        """ Adjustable convention"""
        _keywordChecker([("posType", posType, _posTypes)])
        if posType == "user":
            return self._motor.set(value)


def _keywordChecker(kw_key_list_tups):
    for tkw, tkey, tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s" % (tkw, tlist)



