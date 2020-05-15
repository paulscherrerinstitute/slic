from threading import Thread

from slic.utils import typename

from .basetask import BaseTask


class Task(BaseTask):

    def __init__(self, func, starter=None, stopper=None, hold=True):
        self.func = func
        self.starter = starter
        self.stopper = stopper
        self.thread = Thread(target=self.target)
        self.result = None
        self.exception = None
        if not hold:
            self.start()

    def target(self):
        try:
            self.result = self.func()
        except BaseException as exc: # BaseException covers a few more cases than Exception
            self.exception = exc

    def start(self):
        if self.starter:
            self.starter()
        self.thread.start()

    def stop(self):
        if self.stopper:
            self.stopper()
        return self.wait()

    def wait(self):
        self.thread.join()
        if self.exception:
            raise TaskError from self.exception
        return self.result

    @property
    def status(self):
        if self.thread.ident is None:
            return "ready"
        if self.thread.isAlive():
            return "running"
        return "done"

    def __repr__(self):
        name = typename(self)
        return "{}: {}".format(name, self.status)



class TaskError(RuntimeError):
    def __init__(self):
        message = "Exception in Task"
        super().__init__(message)



