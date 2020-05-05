import os
from abc import abstractmethod

from slic.utils.channels import Channels
from slic.utils import can_create_file, typename
from slic.core.task import Task
from .baseacquisition import BaseAcquisition
from .utils import fix_hdf5_filename
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
            default_dir = self.paths.raw

        self.default_channels = default_channels
        self.default_dir = default_dir


    def acquire(self, filename=None, channels=None, use_default_dir=True, **kwargs):
        if filename and use_default_dir:
            filename = os.path.join(self.default_dir, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        acq = lambda: self._acquire(filename, channels, **kwargs)
        return Task(acq, hold=False)


    @abstractmethod
    def _acquire(self):
        raise NotImplementedError


    def __repr__(self):
        name = typename(self)
        return "{}: {}/{}".format(name, self.instrument, self.pgroup) #TODO



