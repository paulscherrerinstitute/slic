from threading import Thread


class Changer:
    def __init__(self, target=None, parent=None, changer=None, hold=True, stopper=None):
        self.target = target
        self._changer = changer
        self._stopper = stopper
        self._thread = Thread(target=self._changer,args=(target,))
        if not hold:
            self._thread.start()

    def wait(self):
        self._thread.join()

    def start(self):
        self._thread.start()

    def status(self):
        if self._thread.ident is None:
            return 'waiting'
        else:
            if self._thread.isAlive:
                return 'changing'
            else:
                return 'done'
    def stop(self):
        self._stopper()
