from threading import Thread

from slic.utils import typename
from slic.utils.exceptions import ChainedException

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

    def run(self):
        self.start()
        return self.wait()

    def start(self):
        if self.starter:
            self.starter()
        self.thread.start()

    def stop(self):
        if self.stopper:
            self.stopper()
        return self.wait()

    def wait(self):
        try:
            staggered_join(self.thread)
        except KeyboardInterrupt:
            print() # print new line after ^C
            if self.stopper:
                self.stopper()
            self.thread.join() #TODO: should this timeout?
            raise
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



class TaskError(ChainedException):
    def __init__(self):
        message = "Exception in Task"
        super().__init__(message)



def staggered_join(thread, timeout=1):
    """
    Continuously join for timeout seconds to not block KeyboardInterrupt
    """
    while thread.is_alive():
        thread.join(timeout)



