from epics import PV
from time import sleep
from slic.core.task import Task


class SmarActRecord:

    def __init__(self, Id, name=None):
        self.Id = Id
        self.name = name
        self._drive = PV(Id + ":DRIVE")
        self._rbv = PV(Id + ":MOTRBV")
        self._hlm = PV(Id + ":HLM")
        self._llm = PV(Id + ":LLM")
        self._status = PV(Id + ":STATUS")
        self._stop = PV(Id + ":STOP.PROC")

    def set_target_value(self, value, hold=False):
        change = lambda: self.move_and_wait(value)
        return Task(change, hold=hold, stopper=self.stop)

    def stop(self):
        self._stop.put(1)

    def within_limits(self, val):
        llm = self._llm.get("VAL")
        hlm = self._hlm.get("VAL")
        return llm <= val <= hlm

    def move_and_wait(self, value, checktime=0.1):
        self._drive.put(value)
        while self._status.get() != 0:
            sleep(checktime)

    def get_current_value(self):
        return self._rbv.get()

    def __repr__(self):
        return "SmarAct at %s" % (self.get_current_value())



class SmarActStage:

    def __init__(self, axes, name=None, z_undulator=None, description=None):
        self.name = name
        self._keys = axes.keys()
        for ax_name, ax_id in axes.items():
            self.__dict__[ax_name] = SmarActRecord(ax_id)

    def __repr__(self):
        return "SmarAct positions\n%s" % "\n".join(["%s: %s" % (key, self.__dict__[key].get_current_value()) for key in self._keys])



