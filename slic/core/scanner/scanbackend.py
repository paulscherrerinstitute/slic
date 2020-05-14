import os

from slic.utils import make_missing_dir
from slic.utils.printing import printable_dict
from slic.utils.ask_yes_no import ask_Yes_no

from .scaninfo import ScanInfo


class ScanBackend:

    def __init__(self, adjustables, values, acquisitions, filename, n_pulses, data_base_dir, scan_info_dir, make_scan_sub_dir, condition):
        self.adjustables = adjustables
        self.values = values
        self.acquisitions = acquisitions
        self.filename = filename
        self.n_pulses_per_step = n_pulses #TODO: to rename or not to rename?
        self.data_base_dir = data_base_dir

        self.scan_info = ScanInfo(filename, scan_info_dir, adjustables, values)

        self.make_scan_sub_dir = make_scan_sub_dir
        self.condition = condition

        self.store_initial_values()


    def scan(self, step_info=None):
        self.store_initial_values()

        do_step = self.do_checked_step if self.condition else self.do_step

        self.create_output_dirs()

        values = self.values
        ntotal = len(values)
        for n, val in enumerate(values):
            print("Scan step {} of {}".format(n, ntotal))
            do_step(n, val, step_info=step_info)

        print("All scan steps done")

        if ask_Yes_no("Move back to initial values"): #TODO: should this be asked or a parameter?
            self.change_to_initial_values()


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

        fn = self.get_filename(n_step)
        step_filenames = self.acquire_all(fn)
        print("Acquisition done")

        self.scan_info.update(step_values, step_readbacks, step_filenames, step_info)


    def create_output_dirs(self):
        make_missing_dir(self.scan_info.base_dir)

        for acq in self.acquisitions:
            default_dir = acq.default_dir
            if default_dir is None:
                continue
            data_dir = default_dir + self.data_base_dir

            if self.make_scan_sub_dir:
                filebase = os.path.basename(self.filename)
                data_dir += filebase

            make_missing_dir(data_dir)


    def get_filename(self, istep):
        filename = os.path.join(self.data_base_dir, self.filename)

        if self.make_scan_sub_dir:
            filebase = os.path.basename(self.filename)
            filename = os.path.join(filename, filebase)

        filename += "_step{:04d}".format(istep)
        return filename


    def acquire_all(self, filename):
        tasks = []
        filenames = []
        for acq in self.acquisitions:
            t = acq.acquire(filename=filename, n_pulses=self.n_pulses_per_step)
            tasks.append(t)
            filenames.extend(t.filenames)

        wait_for_all(tasks)
        return filenames #TODO: returning this is weird


    def print_current_values(self):
        print_all_current_values(self.adjustables)

    def store_initial_values(self):
        self.initial_values = get_all_current_values(self.adjustables)

    def change_to_initial_values(self):
        set_all_target_values_and_wait(self.adjustables, self.initial_values)



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
        t.wait()



