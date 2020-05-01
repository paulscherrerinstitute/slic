from epics import PV
import os
import numpy as np
import time
from slic.task import Task
from ..aliases import Alias
from time import sleep


class PvRecord:
    def __init__(
        self,
        pvsetname,
        pvreadbackname=None,
        accuracy=None,
        sleeptime=0,
        name=None,
        elog=None,
    ):

        #        alias_fields={"setpv": pvsetname, "readback": pvreadbackname},
        #    ):
        self.Id = pvsetname
        self.name = name
        self.alias = Alias(name)
        self.sleeptime = sleeptime
        #        for an, af in alias_fields.items():
        #            self.alias.append(
        #                Alias(an, channel=".".join([pvname, af]), channeltype="CA")
        #            )

        self._pv = PV(self.Id)
        self._currentChange = None
        self.accuracy = accuracy

        if pvreadbackname is None:
            self._pvreadback = PV(self.Id)
        else:
            self._pvreadback = PV(pvreadbackname)

    def get_current_value(self, readback=True):
        if readback:
            currval = self._pvreadback.get()
        if not readback:
            currval = self._pv.get()
        return currval

    def get_moveDone(self):
        """ Adjustable convention"""
        """ 0: moving 1: move done"""
        movedone = 1
        if self.accuracy is not None:
            if (
                np.abs(
                    self.get_current_value(readback=False)
                    - self.get_current_value(readback=True)
                )
                > self.accuracy
            ):
                movedone = 0
        else:
            sleep(self.sleeptime)
        return movedone

    def move(self, value):
        self._pv.put(value)
        time.sleep(0.1)
        while self.get_moveDone() == 0:
            time.sleep(0.1)

    def set_target_value(self, value, hold=False):
        """ Adjustable convention"""
        changer = lambda: self.move(value)
        return Task(changer, hold=hold)

    # spec-inspired convenience methods
    def mv(self, value):
        self._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):

        if self.get_moveDone == 1:
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(readback=False, *args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)

    def wait(self):
        self._currentChange.wait()

    def __repr__(self):
        return "%s is at: %s" % (self.Id, self.get_current_value())
