from threading import Thread

from .baserunner import BaseRunner
from slic.utils import typename


class Runner(BaseRunner):

    def __init__(self, func, stopper=None, hold=True):
        self.func = func
        self.stopper = stopper
        self.thread = Thread(target=func)
        if not hold:
            self.start()

    def start(self):
        self.thread.start()

    def stop(self):
        if self.stopper is not None:
            self.stopper()
        self.thread.join()

    def wait(self):
        self.thread.join()

    @property
    def status(self):
        if self.thread.ident is None:
            return "ready"
        else:
            if self.thread.isAlive():
                return "running"
            else:
                return "done"

    def __repr__(self):
        name = typename(self)
        return "{}: {}".format(name, self.status)



