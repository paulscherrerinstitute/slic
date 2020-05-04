from pathlib import Path


def make_dir(p):
    p = Path(p)
    if p.exists():
        return
    printable = p.absolute().as_posix()
    print(f"Path \"{printable}\" does not exist, will try to create it...")
    p.mkdir(parents=True)
    p.chmod(0o775)


def glob_files(folder, pattern):
    path = Path(folder)
    fnames = path.glob(pattern)
    fnames = filter_files(fnames)
    return fnames

def filter_files(paths):
    return [p for p in paths if p.is_file()]



