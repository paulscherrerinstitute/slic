from threading import Thread


class Changer:

    def __init__(self, target, changer, stopper=None, hold=True):
        self.target = target
        self.changer = changer
        self.stopper = stopper
        self.thread = Thread(target=changer, args=(target,))
        if not hold:
            self.thread.start()

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
                return "changing"
            else:
                return "done"

    def __repr__(self):
        return "Changer: {}".format(self.status)



