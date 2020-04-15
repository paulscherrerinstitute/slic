from pathlib import Path


EVERYTHING = "*"
DIGITS = "[0-9]"


class RunFilenameGenerator:

    def __init__(self, path, prefix="run", n_digits=4, separator="_", extension="json"):
        self.path = path
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
        fnames = glob_files(self.path, self.pattern)
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

def glob_files(path, pattern):
    path = Path(path)
    fnames = path.glob(pattern)
    fnames = filter_files(fnames)
    return fnames

def filter_files(paths):
    return [p for p in paths if p.is_file()]

def extract_runnumbers(fnames, *args):
    return [extract_runnumber(fn, *args) for fn in fnames]

def extract_runnumber(fname, prefix, separator):
    name = Path(fname).name
    front = name.split(separator)[0]
    runnum = front[len(prefix):]
    runnum = int(runnum)
    return runnum



