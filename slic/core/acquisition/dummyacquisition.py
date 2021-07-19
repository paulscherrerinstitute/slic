from time import sleep
from tqdm import trange

from .acquisition import Acquisition


class DummyAcquisition(Acquisition):

    def _acquire(self, filename, channels=None, data_base_dir=None, scan_info=None, n_pulses=100, **kwargs):
        print("extra kwargs:", kwargs)
        args = (filename, n_pulses, channels)
        args = ", ".join(repr(i) for i in args)
        print("acquire({})".format(args))
        print(f"dummy acquire to {filename}:")
        for i in trange(n_pulses):
            sleep(1/100)



