from functools import wraps
from slic.utils import forwards_to
from .task import Task


class TaskProducer:

    #TODO: allow more than one current_task?
    current_task = None


    def _task_producer(self, func, starter=None, stopper=None):
        @forwards_to(func, nfilled=1) # nfilled=1 to remove self
        @wraps(func)
        def wrapper(*args, hold=False, **kwargs):
            filled_func = lambda: func(*args, **kwargs)
            return self._as_task(filled_func, starter=starter, stopper=stopper, hold=hold)

        def task_start():
            if self.current_task:
                return self.current_task.start()

        def task_stop():
            if self.current_task:
                return self.current_task.stop()

        def task_wait(self):
            if self.current_task:
                return self.current_task.wait()

        return wrapper, task_start, task_stop, task_wait


    def _as_task(self, *args, **kwargs):
        self.current_task = task = Task(*args, **kwargs)
        return task



