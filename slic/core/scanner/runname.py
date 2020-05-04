from pathlib import Path

from slic.utils import glob_files


EVERYTHING = "*"
DIGITS = "[0-9]"



class RunFilenameGenerator:

    def __init__(self, base_dir, prefix="run", n_digits=4, separator="_", extension="json"):
        self.base_dir = base_dir
        self.prefix = prefix
        self.n_digits = n_digits
        self.separator = separator
        self.extension = extension

    def get_next_run_filename(self, name):
        runnums = self.get_existing_runnumbers()
        irun = next_int(runnums)
        formatted_irun = zero_pad(irun, self.n_digits)
        return _fill_filename_pattern(name, formatted_irun)

    def get_existing_runnumbers(self):
        fnames = glob_files(self.base_dir, self.pattern)
        runnums = extract_runnumbers(fnames, self.prefix, self.separator)
        return runnums

    @property
    def pattern(self):
        runnum_pattern = self.n_digits * DIGITS
        return _fill_filename_pattern(EVERYTHING, runnum_pattern)

    def _fill_filename_pattern(name, run_index):
        return self.prefix + run_index + self.separator + name + "." + self.extension



def next_int(nums):
    if nums:
        return max(nums) + 1
    else:
        return 0

def zero_pad(i, n):
    return str(i).zfill(n)


def extract_runnumbers(fnames, *args):
    return [extract_runnumber(fn, *args) for fn in fnames]

def extract_runnumber(fname, prefix, separator):
    name = Path(fname).name
    front = name.split(separator)[0]
    runnum = front[len(prefix):]
    runnum = int(runnum)
    return runnum



