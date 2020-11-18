from time import sleep

from slic.core.task import DAQTask
from slic.utils import typename

from .baseacquisition import BaseAcquisition


class FakeAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup):
        self.instrument = instrument
        self.pgroup = pgroup
        self._stop()


    def acquire(self, filename, detectors=None, channels=None, pvs=None, scan_info=None, n_pulses=100, wait=True):

        def _acquire():
            args = (filename, n_pulses)
            args = ", ".join(repr(i) for i in args)
            print("acquire({})".format(args))
            self.running = True
            for i in range(n_pulses):
                if not self.running:
                    break
                print(f"acquire to {filename}: pulse {i}")
                sleep(0.1)

        task = DAQTask(_acquire, stopper=self._stop, filename=filename, hold=False)
        self.current_task = task

        if wait:
            try:
                task.wait()
            except KeyboardInterrupt:
                print("Stopped current DAQ task:")

        return task


    def _stop(self):
        self.running = False


    def __repr__(self):
        return typename(self)



