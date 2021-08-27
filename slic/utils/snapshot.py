from slic.core.adjustable import Adjustable
from .registry import instances


def snapshot(include_internal=False, sort_key=repr):
    """
    returns a list containing all currently defined Adjustables
    by default excluding those defined as internal and
    sorted according to sort_key

    alternative sorting keys could be:
      - sort_key = str
      - sort_key = lambda a: a.ID
      - sort_key = lambda a: a.name
      - ...
    """
    adjs = instances(Adjustable)
    res = (a for a in adjs if include_internal or not a.internal)
    return sorted(res, key=sort_key)



