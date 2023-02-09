from slic.core.adjustable import Adjustable
from .registry import instances


def ensure_adjs(xs):
    return tuple(ensure_adj(x) for x in xs)

def ensure_adj(x):
    if isinstance(x, str):
        x = get_adj(x)
    return x

def get_adj(name):
    adjs = instances(Adjustable)
    for a in adjs:
        if a.name == name:
            return a
    raise ValueError(f"could not find Adjustable with name \"{name}\"")

def get_adjs(include_internal=False):
    adjs = instances(Adjustable)
    return {i.name: i for i in adjs if include_internal or not i.internal}



