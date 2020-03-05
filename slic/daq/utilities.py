from threading import Thread


class Acquisition:

    def __init__(self, acquire, stopper=None, hold=True):
        self._stopper = stopper
        self._thread = Thread(target=acquire)
        if not hold:
            self.start()

    def start(self):
        self._thread.start()

    def stop(self):
        if self._stopper is not None:
            self._stopper()

    def wait(self):
        self._thread.join()

    @property
    def status(self):
        if self._thread.ident is None:
            return "waiting"
        else:
            if self._thread.isAlive():
                return "acquiring"
            else:
                return "done"

    def __repr__(self):
        return "Acquisition {}".format(self.status)



