from pathlib import Path
from slic.utils import json_save, json_load
from slic.gui import widgets as ws
from slic.gui.special import ValueEntry


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
        self.values = {}


    def store(self):
        self._get()
        json_save(self.values, self.fname)

    def load(self):
        self.values = json_load(self.fname)
        self._set()


    def _get(self):
        children = self.get_good_children()
        for child in children:
            value = child.GetValue()
            name = get_long_name(child)
#            print(name, value, sep="\t")
            self.values[name] = value

    def _set(self):
        children = self.get_good_children()
        for child in children:
            name = get_long_name(child)
            try:
                value = self.values[name]
            except KeyError:
                print(f"Warning: cannot load previous value for: {name}")
            else:
                child.SetValue(value)


    def get_good_children(self):
        return list(c for c in recurse(self.managed) if isinstance(c, ws.PersistableWidget))



def recurse_all(objs):
    for obj in objs:
        yield from recurse(obj)

def recurse(obj):
    children = obj.GetChildren()
    if children:
        yield from recurse_all(children)
    else:
        yield obj



def get_long_name(obj):
    lineage = get_lineage(obj)
    names = [g.GetName() for g in lineage]
    name = "\\".join(escape_backslash(n) for n in reversed(names))
    return name

def get_lineage(obj):
    lineage = []
    while obj:
        lineage.append(obj)
        obj = obj.GetParent()
    return lineage

def escape_backslash(s):
    return repr(s)[1:-1]



