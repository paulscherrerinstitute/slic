import os
import colorama

from ..utils import json_dump, make_dir
from ..utils.printing import printable_dict
from ..utils.ask_yes_no import ask_Yes_no



class ScanBackend:

    def __init__(self, adjustables, values, counters, filename, n_pulses, data_base_dir, scan_info_dir, make_scan_sub_dir, checker, checker_sleep_time=0.2):
        self.adjustables = adjustables
        self.values = values
        self.counters = counters
        self.filename = filename
        self.n_pulses_per_step = n_pulses #TODO: to rename or not to rename?
        self.data_base_dir = data_base_dir

        self.scan_info = ScanInfo(filename, scan_info_dir, adjustables, values)

        self.make_scan_sub_dir = make_scan_sub_dir
        self.checker = checker
        self.checker_sleep_time = checker_sleep_time

        self.store_initial_values()


    def scan(self, step_info=None):
        self.store_initial_values()

        do_step = self.do_checked_step if self.checker else self.do_step

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
            self.checker.get_ready()
            self.do_step(*args, **kwargs)
            if self.checker.is_happy():
                break


    def do_step(self, n_step, step_values, step_info=None):
        set_all_target_values_and_wait(self.adjustables, step_values)
        step_readbacks = get_all_current_values(self.adjustables)
        print("Moved adjustables, starting acquisition")

        fn = self.get_filename(n_step)
        step_filenames = self.acquire_all_counters(fn)
        print("Acquisition done")

        self.scan_info.update(step_values, step_readbacks, step_filenames, step_info)


    def create_output_dirs(self):
        make_dir(self.scan_info.base_dir)

        for counter in self.counters:
            default_dir = counter.default_dir
            if default_dir is None:
                continue
            data_dir = default_dir + self.data_base_dir
            make_dir(data_dir)


    def get_filename(self, istep):
        filename = os.path.join(self.data_base_dir, self.filename)

        if self.make_scan_sub_dir:
            filebase = os.path.basename(self.filename)
            filename = os.path.join(filename, filebase)

        filename += "_step{:04d}".format(istep)
        return filename


    def acquire_all_counters(self, filename):
        acqs = []
        filenames = []
        for ctr in self.counters:
            acq = ctr.acquire(filename=filename, n_pulses=self.n_pulses_per_step)
            acqs.append(acq)
            filenames.extend(acq.filenames)

        wait_for_all(acqs)
        return filenames #TODO: returning this is weird


    def print_current_values(self):
        print_all_current_values(self.adjustables)

    def store_initial_values(self):
        self.initial_values = get_all_current_values(self.adjustables)

    def change_to_initial_values(self):
        set_all_target_values_and_wait(self.adjustables, self.initial_values)



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
    changers = set_all_target_values(adjustables, values)
    wait_for_all(changers)

def set_all_target_values(adjustables, values):
    return [adj.set_target_value(val) for adj, val in zip(adjustables, values)]

def wait_for_all(tasks):
    for t in tasks:
        t.wait()



class ScanInfo:

    def __init__(self, filename_base, base_dir, adjustables, values):
        self.base_dir = base_dir
        self.filename = os.path.join(base_dir, filename_base)
        self.filename += "_scan_info.json"

        names = [ta.name if hasattr(ta, "name") else "noName" for ta in adjustables] #TODO else None?
        ids =   [ta.Id   if hasattr(ta, "Id")   else "noId"   for ta in adjustables]
        self.parameters = {"name": names, "Id": ids}

        self.values_all = values

        self.values = []
        self.readbacks = []
        self.files = []
        self.info = []


    def update(self, *args):
        self.append(*args)
        self.write()

    def append(self, values, readbacks, files, info):
        if callable(info):
            info = info()
        self.values.append(values)
        self.readbacks.append(readbacks)
        self.files.append(files)
        self.info.append(info)

    def write(self):
        json_dump(self.to_dict(), self.filename)

    def to_dict(self):
        scan_info_dict = {
            "scan_parameters": self.parameters,
            "scan_values_all": self.values_all,
            "scan_values":     self.values,
            "scan_readbacks":  self.readbacks,
            "scan_files":      self.files,
            "scan_info":       self.info
        }
        return scan_info_dict

    def __str__(self):
        return "Scan info in {}".format(self.filename)



