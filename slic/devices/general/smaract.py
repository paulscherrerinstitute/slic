from epics import PV
from time import sleep
from slic.core.task import Task


class SmarActRecord:

    def __init__(self, Id, name=None, elog=None):
        self.Id = Id
        self._drive = PV(Id + ":DRIVE")
        self._rbv = PV(Id + ":MOTRBV")
        self._hlm = PV(Id + ":HLM")
        self._llm = PV(Id + ":LLM")
        self._status = PV(Id + ":STATUS")
        self._stop = PV(Id + ":STOP.PROC")
        self._twv = PV(Id + ":TWV")
        self._elog = elog
        self.name = name

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold, stopper=self._stop.put(1))

    def stop(self):
        self._stop.put(1)

    def within_limits(self, val):
        return val <= self._hlm.get("VAL") and val >= self._llm.get("VAL")

    def move_and_wait(self, value, checktime=0.1):
        self._drive.put(value)
        while self._status.get() != 0:
            sleep(checktime)

    def get_current_value(self):
        return self._rbv.get()

    wm = get_current_value

    def __str__(self):
        return "SmarAct is at %s" % (self.get_current_value())

    def __repr__(self):
        return self.__str__()



class SmarActStage:

    def __init__(self, axes, name=None, z_undulator=None, description=None):
        self._keys = axes.keys()
        for axis in self._keys:
            ax = axes[axis]
            ax = SmarActRecord(ax)
            self.__dict__[axis] = ax
        self.name = name

    def __str__(self):
        return "SmarAct positions\n%s" % "\n".join(["%s: %s" % (key, self.__dict__[key].wm()) for key in self._keys])

    def __repr__(self):
        return str({key: self.__dict__[key].wm() for key in self._keys})



