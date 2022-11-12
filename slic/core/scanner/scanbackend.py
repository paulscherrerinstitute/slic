import os
import colorama

from slic.utils import make_missing_dir, printable_exception, xrange
from slic.utils.printing import printable_dict, itemize, format_header, printable_table
from slic.utils.ask_yes_no import ask_Yes_no
from slic.utils.trinary import check_trinary

from .runname import RunFilenameGenerator
from .scaninfo import ScanInfo


#SFDAQ: these are used for treating sf_daq differently
from slic.core.acquisition import SFAcquisition
from slic.core.acquisition.fakeacquisition import FakeAcquisition

def is_sfdaq(acq):
    return isinstance(acq, (SFAcquisition, FakeAcquisition))

def is_only_sfdaq(acquisitions):
    return all(is_sfdaq(acq) for acq in acquisitions)



class ScanBackend:

    def __init__(self, adjustables, values, acquisitions, filename, detectors, channels, pvs, n_pulses, data_base_dir, scan_info_dir, make_scan_sub_dir, condition, return_to_initial_values, n_repeat):
        self.adjustables = adjustables
        self.values = values
        self.acquisitions = acquisitions

        #SFDAQ: sf_daq takes the raw filename
        self.filename_sfdaq = filename_sfdaq = filename

        if not is_only_sfdaq(acquisitions):
            #SFDAQ: others use the modified filename
            filename_generator = RunFilenameGenerator(scan_info_dir)
            filename = filename_generator.get_next_run_filename(filename)

        self.filename = filename

        self.detectors = detectors #SFDAQ: only for sf_daq (see also in arguments)
        self.channels = channels
        self.pvs = pvs #SFDAQ: only for sf_daq (see also in arguments)

        self.n_pulses_per_step = n_pulses #TODO: to rename or not to rename?
        self.data_base_dir = data_base_dir

        self.scan_info       = ScanInfo(filename,       scan_info_dir, adjustables, values)
        self.scan_info_sfdaq = ScanInfo(filename_sfdaq, scan_info_dir, adjustables, values)

        self.make_scan_sub_dir = make_scan_sub_dir
        self.condition = condition

        check_trinary(return_to_initial_values)
        self.return_to_initial_values = return_to_initial_values

        self.n_repeat = n_repeat

        self.store_initial_values()

        self.running = False
        self.current_tasks = []


    def run(self, step_info=None):
        self.store_initial_values()
        self.create_output_dirs()

        scan_loop = self.scan_loop if self.n_repeat == 1 else self.repeated_scan_loop

        self.running = True

        try:
            scan_loop(step_info=step_info)
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                print() # print new line after ^C
            else:
                print("Stopping because of:", printable_exception(e))
            self.stop()
            print("Stopped current DAQ tasks:")
            for t in self.current_tasks:
                print()
                print(t)
                print()

        self.running = False

        go_back = self.return_to_initial_values

        if go_back is None:
             go_back = ask_Yes_no("Return to initial values")

        if go_back:
            print("Returning to initial values")
            self.change_to_initial_values()


    def repeated_scan_loop(self, step_info=None):
        base_fn       = self.filename
        base_fn_sfdaq = self.filename_sfdaq

        nreps = self.n_repeat
        for i in xrange(nreps):
            if not self.running:
                break
            print("Repetition {} of {}".format(i+1, "∞" if nreps is None else nreps))
            suffix = f"_{i+1:03}"

            fn       = base_fn       + suffix
            fn_sfdaq = base_fn_sfdaq + suffix

            #TODO: this needs work!
            self.filename       = self.scan_info.filename_base       = fn
            self.filename_sfdaq = self.scan_info_sfdaq.filename_base = fn_sfdaq

            print("File:", fn, fn_sfdaq)
            self.scan_loop(step_info=step_info)

        self.filename       = base_fn
        self.filename_sfdaq = base_fn_sfdaq


    def scan_loop(self, step_info=None):
        do_step = self.do_checked_step if self.condition else self.do_step

        #TODO this needs work
        for acq in self.acquisitions:
            if is_sfdaq(acq):
                run_number = acq.client.next_run()
                print(f"Advanced run number to {run_number} for {acq}.")

        values = self.values
        ntotal = len(values)
        for n, val in enumerate(values):
            if not self.running:
                n -= 1 # stopped before this iteration
                break
            print(colorama.Fore.GREEN, end="")
            print("Scan step {} of {}".format(n+1, ntotal))
            print(colorama.Fore.RESET, end="")
            do_step(n, val, step_info=step_info)

        if self.running and n+1 == ntotal:
            print(colorama.Fore.GREEN, end="")
            print("All scan steps done")
            print(colorama.Fore.RESET, end="")
        else:
            print(colorama.Fore.RED, end="")
            print("Stopped during scan step {} of {}".format(n+1, ntotal))
            print(colorama.Fore.RESET, end="")


    def do_checked_step(self, *args, **kwargs):
        while self.condition.wants_repeat():
            if self.running:
                self.do_step(*args, **kwargs)


    def do_step(self, n_step, step_values, step_info=None):
        set_all_target_values_and_wait(self.adjustables, step_values)
        step_readbacks = get_all_current_values(self.adjustables)
        print("Moved adjustables, starting acquisition")

        #SFDAQ: sf_daq needs scan info in advance, filenames are not needed
        self.scan_info_sfdaq.append(step_values, step_readbacks, None, step_info)

        fn = self.get_filename(n_step)
        step_filenames = self.acquire_all(fn)
        print("Acquisition done")

        if is_only_sfdaq(self.acquisitions):
            #SFDAQ: sf_daq writes scan info to /raw -> skip writing it to /res
            self.scan_info.append(step_values, step_readbacks, step_filenames, step_info)
        else:
            #SFDAQ: if any others, also write scan info to /res
            self.scan_info.update(step_values, step_readbacks, step_filenames, step_info)


    def create_output_dirs(self):
        if not is_only_sfdaq(self.acquisitions):
            #SFDAQ: if any others, prepare writing scan info to /res
            make_missing_dir(self.scan_info.base_dir)

        for acq in self.acquisitions:
            if is_sfdaq(acq):
                #SFDAQ: not needed for sf_daq, but for other methods...
                continue

            default_dir = acq.default_dir
            if default_dir is None:
                continue

            data_dir = os.path.join(default_dir, self.data_base_dir)

            if self.make_scan_sub_dir:
                filebase = os.path.basename(self.filename)
                data_dir = os.path.join(data_dir, filebase)

            make_missing_dir(data_dir)


    def get_filename(self, istep):
        #SFDAQ: the modified filename is not used for sf_daq
        filename = self.filename

        if self.make_scan_sub_dir:
            filebase = os.path.basename(self.filename)
            filename = os.path.join(filename, filebase)

        filename += "_step{:04d}".format(istep)
        return filename


    def acquire_all(self, filename):
        tasks = []
        for acq in self.acquisitions:
            if is_sfdaq(acq):
                #SFDAQ: sf_daq expects scan info in advance, detectors/bs-channels/PVs separated, raw filename without counters
                scan_info = self.scan_info_sfdaq.to_sfdaq_dict()
                t = acq.acquire(self.filename_sfdaq, data_base_dir=self.data_base_dir, detectors=self.detectors, channels=self.channels, pvs=self.pvs, scan_info=scan_info, n_pulses=self.n_pulses_per_step, is_scan_step=True, wait=False)
            else:
                #SFDAQ: others do not expect scan info at all, expect only one type of channels, filename (which is optional) is used verbatim, i.e., needs to have counters and scan sub dir
                t = acq.acquire(filename=filename, data_base_dir=self.data_base_dir, channels=self.channels, n_pulses=self.n_pulses_per_step, wait=False)
            tasks.append(t)

        self.current_tasks = tasks
        wait_for_all(tasks)

        filenames = []
        for t in tasks:
            filenames.extend(t.filenames)
            print(t)

        return filenames #TODO: returning this is weird


    def print_current_values(self):
        print_all_current_values(self.adjustables)

    def store_initial_values(self):
        self.initial_values = get_all_current_values(self.adjustables)

    def change_to_initial_values(self):
        set_all_target_values_and_wait(self.adjustables, self.initial_values)

    def stop(self):
        self.running = False
        stop_all(self.current_tasks)
        if self.condition:
            self.condition.stop()


    def __repr__(self):
        return self._make_summary(enumerate_lines=True, make_legend=True)

    def summarize(self, enumerate_lines=True, make_legend=True):
        print(self._make_summary(enumerate_lines=enumerate_lines, make_legend=make_legend))

    def _make_summary(self, **kwargs):
        res = ""

        nreps = self.n_repeat
        if nreps is None:
            printable_nreps = "repeat the following scan forever"
        elif nreps == 1:
            printable_nreps = "perform the following scan"
        else:
            printable_nreps = f"repeat the following scan {nreps} times"
        res += format_header(printable_nreps, line="=") + "\n\n"

        vals = self.values
        adjs = [repr(a) for a in self.adjustables]
        res += printable_table(vals, adjs, **kwargs)
        res += "\n\n"

        n_pulses_per_step = self.n_pulses_per_step
        printable_pulses = f"{n_pulses_per_step} pulse"
        if n_pulses_per_step != 1:
            printable_pulses += "s"

        head = f"record {printable_pulses} per step to \"{self.filename}\" via"
        acqs = itemize(self.acquisitions, header=head)
        res += acqs

        return res



#TODO: add class AdjustableGroup with the below as methods?

def print_all_current_values(adjustables):
    res = {}
    for adj in adjustables:
        key = adj.ID
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

def wait_for_all(tasks): #TODO: do we need to stagger the waiting here (to raise all exceptions ASAP)?
    for t in tasks:
        t.wait()

def stop_all(tasks):
    for t in tasks:
        try:
            t.stop()
        except Exception as e:
            print("Stopping caused:", printable_exception(e))



