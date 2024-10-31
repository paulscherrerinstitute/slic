from time import sleep

from slic.utils import pbrange

from .acquisition import Acquisition


class DummyAcquisition(Acquisition):

    def _acquire(self, filename, channels=None, data_base_dir=None, scan_info=None, n_pulses=100, **kwargs):
        print("extra kwargs:", kwargs)
        args = (filename, n_pulses, channels)
        args = ", ".join(repr(i) for i in args)
        print(f"acquire({args})")
        print(f"dummy acquire to {filename}:")
        for i in pbrange(n_pulses, description="Acquiring..."):
            sleep(1/100)



