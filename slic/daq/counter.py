import os
from abc import abstractmethod

from .basecounter import BaseCounter
from .utils import can_create_file, fix_hdf5_filename

from .acquisition import Acquisition



class Counter(BaseCounter):

    def __init__(self, default_channels=None, default_path="."):
        self.default_channels = default_channels
        self.default_path = default_path


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



