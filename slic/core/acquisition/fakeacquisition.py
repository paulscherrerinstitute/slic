import os
import random
from time import sleep
from tqdm import trange

from slic.core.task import DAQTask
from slic.utils import typename

from .baseacquisition import BaseAcquisition


class FakeAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup):
        self.instrument = instrument
        self.pgroup = pgroup

        self.client = FakeClient()

        self.default_data_base_dir = "static_data"
        self.default_dir = ""

        self.default_detectors = shuffle([f"JFJFJFJFJFJFJFJFJFJF{i}" for i in range(2)])
        self.default_channels  = shuffle([f"CHCHCHCHCH{i}" for i in range(100)])
        self.default_pvs       = shuffle([f"PVPV{i}" for i in range(10)])

        self._stop()


    def acquire(self, filename, data_base_dir=None, detectors=None, channels=None, pvs=None, scan_info=None, n_pulses=100, continuous=False, is_scan_step=False, wait=True):
        if not is_scan_step:
            run_number = self.client.next_run()
            print(f"Advanced run number to {run_number}.")
        else:
            run_number = self.client.run_number
            print(f"Continuing run number {run_number}.")

        if data_base_dir is None:
            print("No base directory specified, using default base directory.")
            data_base_dir = self.default_data_base_dir

        filename = os.path.join(data_base_dir, filename)

        def _acquire():
            args = (filename, n_pulses)
            args = ", ".join(repr(i) for i in args)
            print("acquire({})".format(args))
            print(f"fake acquire to {filename}:")
            self.running = True
            n = 0
            while self.running and (continuous or n == 0):
                n += 1
                for i in trange(n_pulses):
                    if not self.running:
                        break
                    sleep(1/100)

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



def shuffle(seq):
    random.shuffle(seq)
    return seq



class FakeClient:

    run_number = 0

    def next_run(self):
        self.run_number += 1
        print("run number is", self.run_number)
        return self.run_number



