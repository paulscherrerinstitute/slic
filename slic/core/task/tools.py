from functools import wraps
from slic.utils import forwards_to
from .task import Task


class TaskProducer:

    current_task = None

    def task_producer(self, func, starter=None, stopper=None):
        @forwards_to(func, nfilled=1) # nfilled=1 to remove self
        @wraps(func)
        def wrapper(*args, hold=False, **kwargs):
            filled_func = lambda: func(*args, **kwargs)
            return self._as_task(filled_func, starter=starter, stopper=stopper, hold=hold)
        return wrapper

    def _as_task(self, *args, **kwargs):
        self.current_task = task = Task(*args, **kwargs)
        return task

    def wait(self):
        if self.current_task:
            return self.current_task.wait()

    def stop(self):
        if self.current_task:
            return self.current_task.stop()



