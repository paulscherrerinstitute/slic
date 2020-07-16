from time import sleep

from epics import PV

from slic.core.task import Task


class PvAdjustable:

    def __init__(self, pvsetname, pvreadbackname=None, accuracy=None, sleeptime=0, name=None):
        self.Id = pvsetname
        self.name = name
        self.sleeptime = sleeptime

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

    def is_moving(self):
        movedone = 1
        if self.accuracy is not None:
            if (
                abs(
                    self.get_current_value(readback=False)
                    - self.get_current_value(readback=True)
                )
                > self.accuracy
            ):
                movedone = 0
        else:
            sleep(self.sleeptime)
        return not bool(movedone)

    def move(self, value):
        self._pv.put(value)
        sleep(0.1)
        while self.is_moving():
            sleep(0.1)

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move(value)
        return Task(changer, hold=hold)


    # spec-inspired convenience methods
    def mv(self, value):
        self._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        if not self.is_moving():
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(readback=False, *args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)

    def wait(self):
        self._currentChange.wait()


    def __repr__(self):
        return "%s is at: %s" % (self.Id, self.get_current_value())



