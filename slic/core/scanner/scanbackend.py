import os

from slic.utils import make_missing_dir
from slic.utils.printing import printable_dict
from slic.utils.ask_yes_no import ask_Yes_no
from slic.utils.trinary import check_trinary

from .scaninfo import ScanInfo


class ScanBackend:

    def __init__(self, adjustables, values, acquisitions, filename, detectors, channels, pvs, n_pulses, data_base_dir, scan_info_dir, make_scan_sub_dir, condition, move_back_to_initial_values):
        self.adjustables = adjustables
        self.values = values
        self.acquisitions = acquisitions
        self.filename = filename

        self.detectors = detectors #TODO: only for sf_daq (see also in arguments)
        self.channels = channels
        self.pvs = pvs #TODO: only for sf_daq (see also in arguments)

        self.n_pulses_per_step = n_pulses #TODO: to rename or not to rename?
        self.data_base_dir = data_base_dir

        self.scan_info       = ScanInfo(filename, scan_info_dir, adjustables, values)
        self.scan_info_sfdaq = ScanInfo(filename, scan_info_dir, adjustables, values)

        self.make_scan_sub_dir = make_scan_sub_dir
        self.condition = condition

        check_trinary(move_back_to_initial_values)
        self.move_back_to_initial_values = move_back_to_initial_values

        self.store_initial_values()

        self.current_tasks = []


    def run(self, step_info=None):
        self.store_initial_values()
        self.create_output_dirs()

        try:
            self.scan_loop(step_info=None)
        except KeyboardInterrupt:
            print() # print new line after ^C
            self.stop()
            print("Stopped current DAQ tasks:")
            for t in self.current_tasks:
                print()
                print(t)
                print()

        move_back = self.move_back_to_initial_values

        if move_back is None:
             move_back = ask_Yes_no("Move back to initial values")

        if move_back:
            print("Moving back to initial values")
            self.change_to_initial_values()


    def scan_loop(self, step_info=None):
        do_step = self.do_checked_step if self.condition else self.do_step

        values = self.values
        ntotal = len(values)
        for n, val in enumerate(values):
            print("Scan step {} of {}".format(n, ntotal))
            do_step(n, val, step_info=step_info)

        print("All scan steps done")


    def do_checked_step(self, *args, **kwargs):
        while True:
            self.condition.get_ready()
            self.do_step(*args, **kwargs)
            if self.condition.is_happy():
                break


    def do_step(self, n_step, step_values, step_info=None):
        set_all_target_values_and_wait(self.adjustables, step_values)
        step_readbacks = get_all_current_values(self.adjustables)
        print("Moved adjustables, starting acquisition")

#TODO: sf_daq needs scan info in advance, filenames are not needed
        self.scan_info_sfdaq.append(step_values, step_readbacks, None, step_info)

        fn = self.get_filename(n_step)
        step_filenames = self.acquire_all(fn)
        print("Acquisition done")

        self.scan_info.update(step_values, step_readbacks, step_filenames, step_info)


    def create_output_dirs(self):
        make_missing_dir(self.scan_info.base_dir)

#TODO: cannot do this anymore for sf_daq, but need it for other methods...
#        for acq in self.acquisitions:
#            default_dir = acq.default_dir
#            if default_dir is None:
#                continue
#            data_dir = os.path.join(default_dir, self.data_base_dir)

#            if self.make_scan_sub_dir:
#                filebase = os.path.basename(self.filename)
#                data_dir = os.path.join(data_dir, filebase)

#            make_missing_dir(data_dir)


    def get_filename(self, istep):
        filename = os.path.join(self.data_base_dir, self.filename)

#TODO: no settable file names in sf_daq, but need it for other methods...
#        if self.make_scan_sub_dir:
#            filebase = os.path.basename(self.filename)
#            filename = os.path.join(filename, filebase)

#TODO: sf_daq counts runs
#        filename += "_step{:04d}".format(istep)
        return filename


    def acquire_all(self, filename):
        tasks = []
        for acq in self.acquisitions:
#TODO: sf_daq expects scan info in advance, and detectors/bs-channels/PVs separated
            scan_info = self.scan_info_sfdaq.to_sfdaq_dict()
            t = acq.acquire(filename, detectors=self.detectors, channels=self.channels, pvs=self.pvs, scan_info=scan_info, n_pulses=self.n_pulses_per_step, wait=False)
#            t = acq.acquire(filename=filename, channels=self.channels, n_pulses=self.n_pulses_per_step, wait=False)
            tasks.append(t)

        self.current_tasks = tasks
        wait_for_all(tasks)

        filenames = []
        for t in tasks:
            filenames.extend(t.filenames)

        return filenames #TODO: returning this is weird


    def print_current_values(self):
        print_all_current_values(self.adjustables)

    def store_initial_values(self):
        self.initial_values = get_all_current_values(self.adjustables)

    def change_to_initial_values(self):
        set_all_target_values_and_wait(self.adjustables, self.initial_values)

    def stop(self):
        stop_all(self.current_tasks)



#TODO: add class AdjustableGroup with the below as methods?

def print_all_current_values(adjustables):
    res = {}
    for adj in adjustables:
        key = adj.Id
        val = adj.get_current_value()
        res[key] = val
    res = printable_dict(res, "Current values")
    print(res)

def get_all_current_values(adjustables):
    return [adj.get_current_value() for adj in adjustables]

def set_all_target_values_and_wait(adjustables, values):
    tasks = set_all_target_values(adjustables, values)
    wait_for_all(tasks)

def set_all_target_values(adjustables, values):
    return [adj.set_target_value(val) for adj, val in zip(adjustables, values)]

def wait_for_all(tasks):
    for t in tasks:
        try: # TODO: what do we want to do here? not write the filenames(s?) to scan_info?
            t.wait()
        except KeyboardInterrupt:
            raise
        except Exception as e: #TODO: should this just be TaskError?
            print(e)

def stop_all(tasks):
    for t in tasks:
        try:
            t.stop()
        except Exception as e:
            print(e)



