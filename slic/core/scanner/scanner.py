import numpy as np

from slic.core.adjustable import DummyAdjustable
from slic.utils import typename, nice_linspace, nice_arange

from .scanbackend import ScanBackend
from .runname import RunFilenameGenerator


make_positions = nice_linspace


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
    def make_scan(self, adjustables, positions, n_pulses, filename, detectors=None, channels=None, pvs=None, acquisitions=(), start_immediately=True, step_info=None, return_to_initial_values=None):
        """N-dimensional scan

        Parameters:
            adjustables (sequence of BaseAdjustables): Adjustables to scan.
            positions (sequence of sequences): One sequence of positions to iterate through for each adjustable.
            n_pulses (int): Number of pulses per step.
            channels (sequence of strings, optional): List of channels to acquire. If None (default), the default lists of the acquisitions will be used.
            acquisitions (sequence of BaseAcquisitions, optional): List of acquisition objects to acquire from. If empty (default) the default list will be used.
            start_immediately (bool, optional): If True (default), start the scan immediately. If False, the returned scan can be started via its run method.
            step_info: Arbitraty data that is appended to the ScanInfo in each step.
            return_to_initial_values: (bool or None, optional): Return to initial values after scan. If None (default) ask for user input.

        Returns:
            ScanBackend: Scan instance.
        """
#TODO: sf_daq counts runs
#        filename = self.filename_generator.get_next_run_filename(filename)

        if not acquisitions:
            acquisitions = self.default_acquisitions

#TODO: detectors and pvs only for sf_daq
        scan = ScanBackend(adjustables, positions, acquisitions, filename, detectors, channels, pvs, n_pulses=n_pulses, data_base_dir=self.data_base_dir, scan_info_dir=self.scan_info_dir, make_scan_sub_dir=self.make_scan_sub_dir, condition=self.condition, return_to_initial_values=return_to_initial_values)

        if start_immediately:
            scan.run(step_info=step_info)

        self.current_scan = scan
        return scan


    def scan1D(self, adjustable, start_pos, end_pos, step_size, *args, relative=False, **kwargs):
        """One-dimensional scan

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            start_pos (number): Starting position
            end_pos (number): End position
            step_size (number): Size of each step
            relative (bool, optional): Positions relative to current position of adjustable (in contrast to absolute)
            args: are forwarded to make_scan()
            kwargs: are forwarded to make_scan()

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable]

        if relative:
            current = adjustable.get_current_value()
            start_pos += current
            end_pos   += current

        positions = nice_arange(start_pos, end_pos, step_size)
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def scan2D(self, adjustable1, start_pos1, end_pos1, step_size1, adjustable2, start_pos2, end_pos2, step_size2, *args, relative1=False, relative2=False, **kwargs):
        """Two-dimensional scan

        Parameters:
            adjustable1 (BaseAdjustable): First Adjustable to scan
            start_pos1 (number): Starting position of first Adjustable
            end_pos1 (number): End position of first Adjustable
            step_size1 (number): Size of each step for first Adjustable
            relative1 (bool, optional): Positions relative to current position of adjustable1 (in contrast to absolute)

            adjustable2 (BaseAdjustable): Second Adjustable to scan
            start_pos2 (number): Starting position of second Adjustable
            end_pos2 (number): End position of second Adjustable
            step_size2 (number): Size of each step for second Adjustable
            relative2 (bool, optional): Positions relative to current position of adjustable2 (in contrast to absolute)

            args: are forwarded to make_scan()
            kwargs: are forwarded to make_scan()

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable1, adjustable2]

        if relative1:
            current1 = adjustable1.get_current_value()
            start_pos1 += current1
            end_pos1   += current1

        if relative2:
            current2 = adjustable2.get_current_value()
            start_pos2 += current1
            end_pos2   += current1

        positions1 = nice_arange(start_pos1, end_pos1, step_size1)
        positions2 = nice_arange(start_pos2, end_pos2, step_size2)

        positions = make_2D_pairs(positions1, positions2)

        return self.make_scan(adjustables, positions, *args, **kwargs)


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


    def a2scan(self, adjustable1, start_pos1, end_pos1, adjustable2, start_pos2, end_pos2, n_intervals, *args, **kwargs):
        adjustables = [adjustable1, adjustable2]

        positions1 = make_positions(start_pos1, end_pos1, n_intervals)
        positions2 = make_positions(start_pos2, end_pos2, n_intervals)
        positions = transpose(positions1, positions2)

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


    def a2scan_list(self, adjustable1, positions1, adjustable2, positions2, *args, **kwargs):
        adjustables = [adjustable1, adjustable2]

        positions = transpose(positions1, positions2)

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

def make_2D_pairs(x, y):
    x_grid, y_grid = np.meshgrid(x, y)
    x_flat = x_grid.T.ravel()
    y_flat = y_grid.T.ravel()
    pairs = np.vstack((x_flat, y_flat)).T
    return pairs



