from pathlib import Path


def make_dir(p):
    p = Path(p)
    if p.exists():
        return
    printable = p.absolute().as_posix()
    print(f"Path \"{printable}\" does not exist, will try to create it...")
    p.mkdir(parents=True)
    p.chmod(0o775)



