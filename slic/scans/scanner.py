from pathlib import Path
import numpy as np

from .scansimple import ScanSimple
from .runname import RunFilenameGenerator
from ..devices.general.adjustable import DummyAdjustable



def make_dir(p):
    p = Path(p)
    if p.exists():
        return
    printable = p.absolute().as_posix()
    print(f"Path \"{printable}\" does not exist, will try to create it...")
#TODO:
#    p.mkdir(parents=True)
#    p.chmod(0o775)



def make_positions(start, end, n):
    return np.linspace(start, end, n + 1)





class Scanner:

    def __init__(self, data_base_dir="", scan_info_dir="", default_counters=[], checker=None, scan_directories=False):
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self.default_counters = default_counters
        self.checker = checker
        self.scan_directories = scan_directories

        make_dir(scan_info_dir)
        self.filename_generator = RunFilenameGenerator(scan_info_dir)

        for counter in default_counters:
            default_path = counter.default_path
            if default_path is None:
                continue
            data_dir = default_path + data_base_dir
            make_dir(data_dir)


    def make_scan(self, adjustables, positions, n_pulses, filename, counters=[], start_immediately=True, step_info=None):

        #TODO
        print(adjustables)#, adjustables.shape, adjustables.dtype)
        print(list(positions))#, positions.shape, positions.dtype)
        return
        #TODO

        filename = self.filename_generator.get_nextrun_filename(filename)

        if not counters:
            counters = self.default_counters

        s = ScanSimple(adjustables, positions, counters, filename, Npulses=n_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self.scan_directories)

        if start_immediately:
            s.scan(step_info=step_info)

        return s


    def ascan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions = zip(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def a2scan(self, adjustable0, start0_pos, end0_pos, adjustable1, start1_pos, end1_pos, n_intervals, *args, **kwargs):
        adjustables = [adjustable0, adjustable1]

        positions0 = make_positions(start0_pos, end0_pos, n_intervals)
        positions1 = make_positions(start1_pos, end1_pos, n_intervals)
        positions = zip(positions0, positions1)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def rscan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions += adjustable.get_current_value()
        positions = zip(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def dscan(self, *args, **kwargs):
        print("Warning: dscan will be deprecated for rscan unless someone explains what it stands for in spec!")
        return self.rscan(*args, **kwargs)


    def ascan_list(self, adjustable, positions, *args, **kwargs):
        adjustables = [adjustable]

        positions = zip(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def a2scan_list(self, adjustable0, positions0, adjustable1, positions1, *args, **kwargs):
        adjustables = [adjustable0, adjustable1]

        positions = zip(positions0, positions1)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def acquire(self, n_intervals, *args, **kwargs):
        adjustable = DummyAdjustable()
        adjustables = [adjustable]

        positions = range(n_intervals)
        positions = zip(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)



