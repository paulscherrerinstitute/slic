from pathlib import Path
from slic.gui import widgets as ws


PERSISTABLE_WIDGETS = (
    ws.MathEntry,
    ws.FilenameEntry
)


def store(*args):
    p = Persistence(*args)
    p.store()

def load(*args):
    p = Persistence(*args)
    p.load()



class Persistence:

    def __init__(self, fname, managed):
        home = Path.home()
        self.fname = home / fname
        self.managed = managed
        self.values = []


    def store(self):
        self._get()
        list_store(self.fname, self.values)

    def load(self):
        self.values = list_load(self.fname)
        self._set()


    def _get(self):
        children = self.get_good_children()
        for child in children:
            value = child.GetValue()
            self.values.append(value)

    def _set(self):
        children = self.get_good_children()
        nchildren = len(children)
        nvalues = len(self.values)
        if nchildren != nvalues:
            raise ValueError(f"got {nchildren} widgets vs. {nvalues} values mismatch")
        for child, value in zip(children, self.values):
            child.SetValue(value)


    def get_good_children(self):
        return list(c for c in recurse(self.managed) if isinstance(c, PERSISTABLE_WIDGETS))



def recurse_all(objs):
    for obj in objs:
        yield from recurse(obj)

def recurse(obj):
    children = obj.GetChildren()
    if children:
        yield from recurse_all(children)
    else:
        yield obj


def list_store(fname, values):
    print("store to", fname)
    with open(fname, "w") as f:
        for v in values:
            f.write(f"{v}\n")

def list_load(fname):
    print("load from", fname)
    values = []
    with open(fname, "r") as f:
        for line in f:
            value = line.strip()
            values.append(value)
    return values



