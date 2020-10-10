import numpy as np

from slic.core.adjustable import DummyAdjustable
from slic.utils import typename

from .scanbackend import ScanBackend
from .runname import RunFilenameGenerator


def make_positions(start, end, n):
    return np.linspace(start, end, n + 1)


class Scanner:
    """
    Scanner contains several different types of scans as methods.
    The methods simply convert the input parameters to parameters for the N-dimensional scan make_scan().
    Each method returns a ScanBackend instance, which contains the actual scan logic.
    """

    def __init__(self, data_base_dir="scan_data", scan_info_dir="", default_acquisitions=(), condition=None, make_scan_sub_dir=True):
        """
        Parameters:
            data_base_dir (string, optional): Subfolder to collect scan data in. Will be appended to the acquisitions' default_dir.
            scan_info_dir (string, optional): Folder to store ScanInfo.
            default_acquisitions (sequence of BaseAcquisitions, optional): List of default acquisition objects to acquire from.
            condition (BaseCondition): Condition that needs to be fullfilled to accept a recorded step of the scan.
            make_scan_sub_dir (bool): If True (default), create a sub folder in data_base_dir in the acquisition's default_dir for each scan: scanname/scanname_step00001.h5. If False, the per-step files will be saved directly to data_base_dir in the acquisition's default_dir
        """
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self.default_acquisitions = default_acquisitions
        self.condition = condition
        self.make_scan_sub_dir = make_scan_sub_dir

        self.filename_generator = RunFilenameGenerator(scan_info_dir)

        self.current_scan = None


#TODO: detectors and pvs only for sf_daq
    def make_scan(self, adjustables, positions, n_pulses, filename, detectors=None, channels=None, pvs=None, acquisitions=(), start_immediately=True, step_info=None, move_back_to_initial_values="ask"):
        """N-dimensional scan

        Parameters:
            adjustables (sequence of BaseAdjustables): Adjustables to scan.
            positions (sequence of sequences): One sequence of positions to iterate through for each adjustable.
            n_pulses (int): Number of pulses per step.
            channels (sequence of strings, optional): List of channels to acquire. If None (default), the default lists of the acquisitions will be used.
            acquisitions (sequence of BaseAcquisitions, optional): List of acquisition objects to acquire from. If empty (default) the default list will be used.
            start_immediately (bool, optional): If True (default), start the scan immediately. If False, the returned scan can be started via its run method.
            step_info: Arbitraty data that is appended to the ScanInfo in each step.

        Returns:
            ScanBackend: Scan instance.
        """
#TODO: sf_daq counts runs
#        filename = self.filename_generator.get_next_run_filename(filename)

        if not acquisitions:
            acquisitions = self.default_acquisitions

#TODO: detectors and pvs only for sf_daq
        scan = ScanBackend(adjustables, positions, acquisitions, filename, detectors, channels, pvs, n_pulses=n_pulses, data_base_dir=self.data_base_dir, scan_info_dir=self.scan_info_dir, make_scan_sub_dir=self.make_scan_sub_dir, condition=self.condition, move_back_to_initial_values=move_back_to_initial_values)

        if start_immediately:
            scan.run(step_info=step_info)

        self.current_scan = scan
        return scan


    def ascan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        """One-dimensional scan

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            start_pos (number): Starting position
            end_pos (number): End position
            n_intervals (int): Number of intervals
            args: are forwarded to make_scan()
            kwargs: are forwarded to make_scan()

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def a2scan(self, adjustable0, start0_pos, end0_pos, adjustable1, start1_pos, end1_pos, n_intervals, *args, **kwargs):
        adjustables = [adjustable0, adjustable1]

        positions0 = make_positions(start0_pos, end0_pos, n_intervals)
        positions1 = make_positions(start1_pos, end1_pos, n_intervals)
        positions = transpose(positions0, positions1)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def rscan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions += adjustable.get_current_value()
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def ascan_list(self, adjustable, positions, *args, **kwargs):
        adjustables = [adjustable]

        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def a2scan_list(self, adjustable0, positions0, adjustable1, positions1, *args, **kwargs):
        adjustables = [adjustable0, adjustable1]

        positions = transpose(positions0, positions1)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def acquire(self, n_intervals, *args, **kwargs):
        dummy = DummyAdjustable()
        adjustables = [dummy]

        positions = range(n_intervals)
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def __repr__(self):
        return typename(self) #TODO



def transpose(*args):
    return list(zip(*args))



