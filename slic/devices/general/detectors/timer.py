from time import time


class Timer:

    def __init__(self, seconds):
        self.seconds = seconds
        self.time_start = None

    def start(self):
        self.time_start = time()

    @property
    def is_done(self):
        if self.seconds = None:
            return None
        if self.time_start is None:
            self.start()
        time_stop = self.time_start + self.seconds
        return time() > time_stop



