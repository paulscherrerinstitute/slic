from pathlib import Path
from slic.utils import json_save, json_load
from slic.gui import widgets as ws
from slic.gui.special import ValueEntry


def save(*args):
    p = Persistence(*args)
    p.save()

def load(*args):
    p = Persistence(*args)
    p.load()



class Persistence:

    def __init__(self, fname, managed):
        home = Path.home()
        self.fname = home / fname
        self.managed = managed

    def save(self):
        values = get_values(self.managed)
        json_save(values, self.fname)

    def load(self):
        values = json_load(self.fname)
        set_values(values, self.managed)



def get_values(obj):
    values = {}
    children = get_good_children(obj)
    for child in children:
        value = child.GetValue()
        name = get_long_name(child)
#        print(name, value, sep="\t")
        values[name] = value
    return values

def set_values(values, obj):
    children = get_good_children(obj)
    for child in children:
        name = get_long_name(child)
        try:
            value = values[name]
        except KeyError:
            print(f"Warning: no previous value for: {name}")
        else:
            child.SetValue(value)



def get_good_children(obj):
    return [c for c in recurse(obj) if isinstance(c, ws.PersistableWidget)]

def recurse(obj):
    children = obj.GetChildren()
    if children:
        yield from recurse_all(children)
    else:
        yield obj

def recurse_all(objs):
    for obj in objs:
        yield from recurse(obj)



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



