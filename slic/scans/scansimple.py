import os
import colorama

from ..utils import json_dump
from ..utils.printing import printable_dict
from ..utils.ask_yes_no import ask_Yes_no



class ScanSimple:

    def __init__(self, adjustables, values, counters, filename, n_pulses=100, basepath="", scan_info_dir="", make_scan_sub_dir=False, checker=None, checker_sleep_time=0.2):
        self.adjustables = adjustables
        self.values = values
        self.counters = counters
        self.filename = filename
        self.n_pulses_per_step = n_pulses #TODO: to rename or not to rename?
        self.basepath = basepath

        self.scan_info = ScanInfo(filename, scan_info_dir, adjustables, values)

        self.make_scan_sub_dir = make_scan_sub_dir
        self.checker = checker
        self.checker_sleep_time = checker_sleep_time

        self.store_initial_values()


    def scan(self, step_info=None):
        self.store_initial_values()

        do_step = self.do_checked_step if self.checker else self.do_step

        values = self.values
        ntotal = len(values)
        for n, val in enumerate(values):
            print("Scan step {} of {}".format(n, ntotal))
            do_step(n, val, step_info=step_info)

        print("All steps done")

        if ask_Yes_no("Move back to initial values"): #TODO: should this be asked or a parameter?
            self.change_to_initial_values()





    def do_checked_step(self, *args, **kwargs):
        while True: #TODO: this needs to move to checker
            first_check = time()
            checker_unhappy = False
            while not self.checker.check_now():
                print(colorama.Fore.RED + f"Condition checker is not happy, waiting for OK conditions since {time()-first_check:5.1f} seconds." + colorama.Fore.RESET, end="\r")
                sleep(self.checker_sleep_time)
                checker_unhappy = True
            if checker_unhappy:
                print(colorama.Fore.RED + f"Condition checker was not happy and waiting for {time()-first_check:5.1f} seconds." + colorama.Fore.RESET)
            self.checker.clear_and_start_counting()

            self.do_step(*args, **kwargs)

            if self.checker.stop_and_analyze():
                break





    def do_step(self, n_step, step_values, step_info=None):
        set_all_target_values_and_wait(self.adjustables, step_values)
        step_readbacks = get_all_current_values(self.adjustables)
        print("Moved adjustables, starting acquisition")

        fn = self.get_filename(n_step)
        step_filenames = self.acquire_all_counters(fn)
        print("Acquisition done")

        self.scan_info.update(step_values, step_readbacks, step_filenames, step_info)


    def get_filename(self, istep):
        filename = os.path.join(self.basepath, self.filename)

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

def wait_for_all(runners):
    for r in runners:
        r.wait()



class ScanInfo:

    def __init__(self, filename_base, path, adjustables, values):
        self.filename = os.path.join(path, filename_base)
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



