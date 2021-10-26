from functools import wraps


def task_producer(obj, func):
    @wraps(func)
    def wrapper(*args, hold=False, **kwargs):
        filled_func = lambda: func(*args, **kwargs)
        return obj._as_task(filled_func, hold=hold)
    return wrapper



