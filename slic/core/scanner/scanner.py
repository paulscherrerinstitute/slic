from functools import wraps
from warnings import warn

import numpy as np

from slic.core.adjustable import DummyAdjustable
from slic.utils import typename, nice_linspace, nice_arange, forwards_to
from slic.core.sensor.remoteplot import RemotePlot
from slic.utils.get_adj import ensure_adjs

from .scanbackend import ScanBackend


make_positions = nice_linspace


def deprecated(replacement, what=None):
    """
    decorator factory to mark a function as deprecated and recommend a replacement.
    informs which replacement should be used instead via
    a warning message prepended to the docstring and
    a DeprecationWarning emitted when the function is run.

    Parameters:
        replacement (function or string): for a function, its __name__ is used in the message; a string is used as is.
        what (string, optional): allows to customize the name of the decorated function in the message.

    Returns:
        decorator to be applied to a to-be-deprecated function
    """
    if not isinstance(replacement, str):
        replacement = replacement.__name__
    def decorator(func):
        old = what or func.__name__
        msg = f"{old} is deprecated, use {replacement} instead."
        @wraps(func)
        def wrapper(*args, **kwargs):
            warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        wrapper.__doc__ = f"Warning: {msg}\n\n{wrapper.__doc__}"
        return wrapper
    return decorator



class Scanner:
    """
    Scanner contains several different types of scans as methods.
    The methods simply convert the input parameters to parameters for the N-dimensional scan make_scan().
    Each method returns a ScanBackend instance, which contains the actual scan logic.
    """

    def __init__(self, data_base_dir="scan_data", scan_info_dir="scan_info", default_acquisitions=(), condition=None, make_scan_sub_dir=True, default_sensor=None, remote_plot=None):
        """
        Parameters:
            data_base_dir (string, optional): Subfolder to collect scan data in. Will be appended to the acquisitions' default_dir.
            scan_info_dir (string, optional): Folder to store ScanInfo.
            default_acquisitions (sequence of BaseAcquisitions, optional): List of default acquisition objects to acquire from.
            condition (BaseCondition, optional): Condition that needs to be fulfilled to accept a recorded step of the scan.
            make_scan_sub_dir (bool, optional): If True (default), create a sub folder in data_base_dir in the acquisition's default_dir for each scan: scanname/scanname_step00001.h5. If False, the per-step files will be saved directly to data_base_dir in the acquisition's default_dir.
            default_sensor: (BaseSensor, optional): Default sensor to read out and plot.
            remote_plot: (RemotePlot, optional): Existing RemotePlot instance. If not given, a new instance will be created sending to localhost:8000.
        """
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self.default_acquisitions = default_acquisitions
        self.condition = condition
        self.make_scan_sub_dir = make_scan_sub_dir

        self.current_scan = None

        self.default_sensor = default_sensor
        self.remote_plot = remote_plot or RemotePlot("localhost", 8000)


    def __dir__(self):
        # hide deprecated scans from tab completion
        deprecated = {"ascan", "a2scan", "rscan", "ascan_list", "a2scan_list"}
        res = super().__dir__()
        res = set(res) - deprecated
        return sorted(res)


    #SFDAQ: detectors and pvs only for sf_daq
    def make_scan(self, adjustables, positions, n_pulses, filename, detectors=None, channels=None, pvs=None, acquisitions=(), start_immediately=True, step_info=None, return_to_initial_values=None, n_repeat=1, sensor=None):
        """N-dimensional scan

        Parameters:
            adjustables (sequence of BaseAdjustables or strings): Adjustables or Adjustable names to scan.
            positions (sequence of sequences): One sequence of positions to iterate through for each adjustable.
            n_pulses (int): Number of pulses per step.
            filename (str): Name of output file.

            detectors (sequence of strings, optional): List of detectors to acquire. If None (default), the default lists of the acquisitions will be used.
            channels (sequence of strings, optional): List of channels to acquire. If None (default), the default lists of the acquisitions will be used.
            pvs (sequence of strings, optional): List of PVs to acquire. If None (default), the default lists of the acquisitions will be used.

            acquisitions (sequence of BaseAcquisitions, optional): List of acquisition objects to acquire from. If empty (default) the default list will be used.
            start_immediately (bool, optional): If True (default), start the scan immediately. If False, the returned scan can be started via its run method.
            step_info: Arbitrary data that is appended to the ScanInfo in each step.
            return_to_initial_values (bool or None, optional): Return to initial values after scan. If None (default) ask for user input.
            n_repeat (int or None, optional): Number of times the scan is repeated. If 1 (default), the filename will be used verbatim. If >1, a three-digit counter will be appended. None is interpreted as infinity.
            sensor (BaseSensor, optional): Sensor to read out and plot.

        Returns:
            ScanBackend: Scan instance.
        """
        adjustables = ensure_adjs(adjustables)

        acquisitions = acquisitions or self.default_acquisitions
        sensor = sensor or self.default_sensor

        #SFDAQ: detectors and pvs only for sf_daq
        scan = ScanBackend(adjustables, positions, acquisitions, filename, detectors, channels, pvs, n_pulses=n_pulses, data_base_dir=self.data_base_dir, scan_info_dir=self.scan_info_dir, make_scan_sub_dir=self.make_scan_sub_dir, condition=self.condition, return_to_initial_values=return_to_initial_values, n_repeat=n_repeat, sensor=sensor, remote_plot=self.remote_plot)

        if start_immediately:
            scan.run(step_info=step_info)

        self.current_scan = scan
        return scan


    @forwards_to(make_scan, nfilled=3)
    def scan1D(self, adjustable, start_pos, end_pos, step_size, *args, relative=False, **kwargs):
        """One-dimensional scan over a range

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            start_pos (number): Starting position
            end_pos (number): End position
            step_size (number): Size of each step
            relative (bool, optional): Positions relative to current position of adjustable (in contrast to absolute)

            All further parameters are forwarded to make_scan() and described there.

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


    @forwards_to(make_scan, nfilled=3)
    def scan2D(self, adjustable1, start_pos1, end_pos1, step_size1, adjustable2, start_pos2, end_pos2, step_size2, *args, relative1=False, relative2=False, **kwargs):
        """Two-dimensional scan over two ranges

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

            All further parameters are forwarded to make_scan() and described there.

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
            start_pos2 += current2
            end_pos2   += current2

        positions1 = nice_arange(start_pos1, end_pos1, step_size1)
        positions2 = nice_arange(start_pos2, end_pos2, step_size2)

        positions = make_2D_pairs(positions1, positions2)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    @forwards_to(make_scan, nfilled=3)
    def scan1D_seq(self, adjustable, positions, *args, **kwargs):
        """One-dimensional scan over a sequence of positions

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            positions (sequence of numbers): Sequence of positions for adjustable to iterate through

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable]

        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    @forwards_to(make_scan, nfilled=3)
    def scan2D_seq(self, adjustable1, positions1, adjustable2, positions2, *args, **kwargs):
        """Two-dimensional scan over two sequences of positions

        Parameters:
            adjustable1 (BaseAdjustable): First Adjustable to scan
            positions1 (sequence of numbers):  Sequence of positions for first Adjustable to iterate through

            adjustable2 (BaseAdjustable): Second Adjustable to scan
            positions2 (sequence of numbers):  Sequence of positions for second Adjustable to iterate through

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable1, adjustable2]

        positions = transpose(positions1, positions2)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    @deprecated(scan1D)
    @forwards_to(make_scan, nfilled=3)
    def ascan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        """Absolute scan

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            start_pos (number): Starting position
            end_pos (number): End position
            n_intervals (int): Number of intervals

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    @deprecated(scan2D)
    @forwards_to(make_scan, nfilled=3)
    def a2scan(self, adjustable1, start_pos1, end_pos1, adjustable2, start_pos2, end_pos2, n_intervals, *args, **kwargs):
        """Absolute scan -- 2 adjustables

        Parameters:
            adjustable1 (BaseAdjustable): First Adjustable to scan
            start_pos1 (number): Starting position of first Adjustable
            end_pos1 (number): End position of first Adjustable

            adjustable2 (BaseAdjustable): Second Adjustable to scan
            start_pos2 (number): Starting position of second Adjustable
            end_pos2 (number): End position of second Adjustable

            n_intervals (int): Number of intervals

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable1, adjustable2]

        positions1 = make_positions(start_pos1, end_pos1, n_intervals)
        positions2 = make_positions(start_pos2, end_pos2, n_intervals)
        positions = transpose(positions1, positions2)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    @deprecated("scan1D(..., relative=True)")
    @forwards_to(make_scan, nfilled=3)
    def rscan(self, adjustable, start_pos, end_pos, n_intervals, *args, **kwargs):
        """Relative scan

        Parameters:
            adjustable (BaseAdjustable): Adjustable to scan
            start_pos (number): Starting position
            end_pos (number): End position
            n_intervals (int): Number of intervals

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        adjustables = [adjustable]

        positions = make_positions(start_pos, end_pos, n_intervals)
        positions += adjustable.get_current_value()
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    ascan_list = deprecated(scan1D_seq, what="ascan_list")(scan1D_seq)
    a2scan_list = deprecated(scan2D_seq, what="a2scan_list")(scan2D_seq)


    @forwards_to(make_scan, nfilled=3)
    def acquire(self, n_intervals, *args, **kwargs):
        """Static acquisition via scan of DummyAdjustable

        Parameters:
            n_intervals (int): Number of intervals (i.e., repetitions)

            All further parameters are forwarded to make_scan() and described there.

        Returns:
            ScanBackend: Scan instance
        """
        dummy = DummyAdjustable()
        adjustables = [dummy]

        positions = range(n_intervals)
        positions = transpose(positions)

        return self.make_scan(adjustables, positions, *args, **kwargs)


    def __repr__(self):
        tn = typename(self)
        used = "\n- ".join(repr(i) for i in self.default_acquisitions + [self.condition])
        return f"{tn} using:\n- {used}"



def transpose(*args):
    return list(zip(*args))

def make_2D_pairs(x, y):
    x_grid, y_grid = np.meshgrid(x, y)
    x_flat = x_grid.T.ravel()
    y_flat = y_grid.T.ravel()
    pairs = np.vstack((x_flat, y_flat)).T
    return pairs



