from threading import Thread


class Acquisition:

    def __init__(self, acquire, stopper=None, hold=True):
        self.stopper = stopper
        self.thread = Thread(target=acquire)
        if not hold:
            self.start()

    def start(self):
        self.thread.start()

    def stop(self):
        if self.stopper is not None:
            self.stopper()

    def wait(self):
        self.thread.join()

    @property
    def status(self):
        if self.thread.ident is None:
            return "ready"
        else:
            if self.thread.isAlive():
                return "acquiring"
            else:
                return "done"

    def __repr__(self):
        return "Acquisition: {}".format(self.status)



