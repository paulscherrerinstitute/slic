from slic.core.adjustable import Adjustable
from .registry import instances


def snapshot(include_internal=False):
    adjs = instances(Adjustable)
    res = [a for a in adjs if include_internal or not a.internal]
    return sorted(res, key=repr)
    return sorted(res, key=lambda x: x.name)



