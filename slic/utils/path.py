import os
from pathlib import Path

from .ask_yes_no import ask_yes_No


def can_create_all_files(filenames):
    for fn in filenames:
        if not can_create_file(fn):
            return False
    return True


def can_create_file(filename):
    if not os.path.isfile(filename):
        return True

    delete = ask_yes_No("File \"{}\" exists already. Would you like to delete it".format(filename))
    if delete:
        print("Deleting \"{}\".".format(filename))
        os.remove(filename)
        return True

    return False


def make_missing_dir(p):
    p = Path(p)
    if p.exists():
        return

    printable = p.absolute().as_posix()
    msg = "Directory \"{}\" does not exist, creating it...".format(printable)
    print(msg)

    p.mkdir(mode=0o775, parents=True, exist_ok=True)


def glob_files(folder, pattern):
    path = Path(folder)
    fnames = path.glob(pattern)
    fnames = filter_files(fnames)
    return fnames

def filter_files(paths):
    return [p for p in paths if p.is_file()]



