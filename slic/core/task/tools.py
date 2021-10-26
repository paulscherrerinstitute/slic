from functools import wraps
from slic.utils import forwards_to


def task_producer(obj, func, starter=None, stopper=None):
    @forwards_to(func, nfilled=1) # nfilled=1 to remove self
    @wraps(func)
    def wrapper(*args, hold=False, **kwargs):
        filled_func = lambda: func(*args, **kwargs)
        return obj._as_task(filled_func, starter=starter, stopper=stopper, hold=hold)
    return wrapper



