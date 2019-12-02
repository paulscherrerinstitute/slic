from threading import Thread

class Acquisition:
    def __init__(self, parent=None, acquire=None, acquisition_kwargs = {}, hold=True, stopper=None):
        self.acquisition_kwargs = acquisition_kwargs
        self.file_names = acquisition_kwargs['file_names']
        self._acquire = acquire
        self._stopper = stopper
        self._thread = Thread(target=self._acquire)
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
            if self._thread.isAlive():
                return 'acquiring'
            else:
                return 'done'
    def stop(self):
        self._stopper()

