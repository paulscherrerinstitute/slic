from pathlib import Path
import numpy as np

from .scansimple import ScanSimple
from ..devices_general.adjustable import DummyAdjustable


class Scanner:

    def __init__(self, data_base_dir="", scan_info_dir="", default_counters=[], checker=None, scan_directories=False):
        self.data_base_dir = data_base_dir
        scan_info_dir = Path(scan_info_dir)
        if not scan_info_dir.exists():
            print(f"Path {scan_info_dir.absolute().as_posix()} does not exist, will try to create it...")
            scan_info_dir.mkdir(parents=True)
            print(f"Tried to create {scan_info_dir.absolute().as_posix()}")
            scan_info_dir.chmod(0o775)
            print(f"Tried to change permissions to 775")

        for counter in default_counters:
            if counter._default_file_path is not None:
                data_dir = Path(counter._default_file_path + self.data_base_dir)
                if not data_dir.exists():
                    print(f"Path {data_dir.absolute().as_posix()} does not exist, will try to create it...")
                    data_dir.mkdir(parents=True)
                    print(f"Tried to create {data_dir.absolute().as_posix()}")
                    data_dir.chmod(0o775)
                    print(f"Tried to change permissions to 775")

        self.scan_info_dir = scan_info_dir
        self.filename_generator = RunFilenameGenerator(self.scan_info_dir)
        self._default_counters = default_counters
        self.checker = checker
        self._scan_directories = scan_directories

    def ascan(self, adjustable, start_pos, end_pos, N_intervals, N_pulses, file_name=None, counters=[], start_immediately=True, step_info=None):
        positions = np.linspace(start_pos, end_pos, N_intervals + 1)
        values = [[tp] for tp in positions]
        file_name = self.filename_generator.get_nextrun_filename(file_name)
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable], values, counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def a2scan(self, adjustable0, start0_pos, end0_pos, adjustable1, start1_pos, end1_pos, N_intervals, N_pulses, file_name=None, counters=[], start_immediately=True, step_info=None):
        positions0 = np.linspace(start0_pos, end0_pos, N_intervals + 1)
        positions1 = np.linspace(start1_pos, end1_pos, N_intervals + 1)
        values = [[tp0, tp1] for tp0, tp1 in zip(positions0, positions1)]
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable0, adjustable1], values, self.counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def rscan(self, adjustable, start_pos, end_pos, N_intervals, N_pulses, file_name=None, counters=[], start_immediately=True, step_info=None):
        positions = np.linspace(start_pos, end_pos, N_intervals + 1)
        current = adjustable.get_current_value()
        values = [[tp + current] for tp in positions]
        file_name = self.filename_generator.get_nextrun_filename(file_name)
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable], values, counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def dscan(self, *args, **kwargs):
        print("Warning: dscan will be deprecated for rscan unless someone explains what it stands for in spec!")
        return self.rscan(*args, **kwargs)

    def ascanList(self, adjustable, posList, N_pulses, file_name=None, counters=[], start_immediately=True, step_info=None):
        positions = posList
        values = [[tp] for tp in positions]
        file_name = self.filename_generator.get_nextrun_filename(file_name)
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable], values, counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def a2scanList(self, adjustable0, start0_pos, end0_pos, adjustable1, start1_pos, end1_pos, N_intervals, N_pulses, file_name=None, counters=[], start_immediately=True, step_info=None):
        positions0 = np.linspace(start0_pos, end0_pos, N_intervals + 1)
        positions1 = posList
        values = [[tp0, tp1] for tp0, tp1 in zip(positions0, positions1)]
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable0, adjustable1], values, self.counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def acquire(self, N_pulses, N_repetitions=1, file_name=None, counters=[], start_immediately=True, step_info=None):
        adjustable = DummyAdjustable()

        positions = list(range(N_repetitions))
        values = [[tp] for tp in positions]
        file_name = self.filename_generator.get_nextrun_filename(file_name)
        if not counters:
            counters = self._default_counters
        s = ScanSimple([adjustable], values, counters, file_name, Npulses=N_pulses, basepath=self.data_base_dir, scan_info_dir=self.scan_info_dir, checker=self.checker, scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s



