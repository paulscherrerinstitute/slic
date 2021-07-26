from pathlib import Path
from slic.utils import typename, json_save, json_load


def skip_on_error(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            fn = f.__name__
            en = typename(e)
            print(f"skipped persist {fn} as it caused: {en}: {e}")
    return wrapper



class PersistableWidget:
    pass



class Persistence:

    def __init__(self, fname, managed):
        home = Path.home()
        self.fname = home / fname
        self.managed = managed

    @skip_on_error
    def save(self):
        values = get_values(self.managed)
        json_save(values, self.fname)

    @skip_on_error
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
    return [c for c in recurse(obj) if isinstance(c, PersistableWidget)]

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



