from pathlib import Path


class DotDir:

    def __init__(self, basename=".slic"):
        home = Path.home()
        self.base = base = home / basename
        base.mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return str(self.base)

    def __call__(self, name):
        return self.base / name



