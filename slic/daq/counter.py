import os
from abc import abstractmethod

from ..utils.channels import Channels
from .acquisition import Acquisition
from .basecounter import BaseCounter
from .utils import can_create_file, fix_hdf5_filename, SwissFELPaths



class Counter(BaseCounter):

    def __init__(self, instrument, pgroup, default_channels=None, default_path=None):
        paths = SwissFELPaths(instrument, pgroup)

        if not default_channels:
            default_channel_list = paths.default_channel_list
            default_channels = Channels(default_channel_list)

        if not default_path:
            default_path = paths.raw


    def acquire(self, filename=None, channels=None, use_default_path=True, **kwargs):
        if filename and use_default_path:
            filename = os.path.join(self.default_path, filename)

        filename = fix_hdf5_filename(filename)

        if not can_create_file(filename):
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        acq = lambda: self._acquire(filename, channels, **kwargs)
        return Acquisition(acq, hold=False)


    @abstractmethod
    def _acquire(self):
        raise NotImplementedError



