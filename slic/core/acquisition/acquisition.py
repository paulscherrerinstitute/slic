import os
from abc import abstractmethod

from slic.utils.channels import Channels
from slic.utils import can_create_file, typename
from slic.core.task import DAQTask

from .baseacquisition import BaseAcquisition
from .sfpaths import SwissFELPaths


class Acquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup, default_channels=None, default_dir=None):
        self.instrument = instrument
        self.pgroup = pgroup

        self.paths = SwissFELPaths(instrument, pgroup)

        if not default_channels:
            default_channel_list = self.paths.default_channel_list
            default_channels = Channels(default_channel_list)

        if not default_dir:
            default_dir = self.paths.res

        self.default_channels = default_channels
        self.default_dir = default_dir

        self.current_task = None


    def acquire(self, filename=None, channels=None, use_default_dir=True, wait=True, **kwargs):
        if filename and use_default_dir:
            filename = os.path.join(self.default_dir, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        acq = lambda: self._acquire(filename, channels, **kwargs)

        task = DAQTask(acq, filename=filename, hold=False)
        self.current_task = task

        if wait:
            task.wait()

        return task


    @abstractmethod
    def _acquire(self):
        raise NotImplementedError


    def __repr__(self):
        name = typename(self)
        return "{}: {}/{}".format(name, self.instrument, self.pgroup) #TODO



def fix_hdf5_filename(filename):
    if filename:
        if not filename.endswith(".h5"):
            filename += ".h5"
    else:
        filename = "/dev/null"
    return filename



