from time import time


class Timer:

    def __init__(self, seconds):
        self.time_stop = time() + seconds

    @property
    def is_done(self):
        return time() > self.time_stop



