from time import sleep
import tqdm


class tqdm_mod(tqdm.tqdm):

    def set(self, elapsed):
        """
        update with elapsed n, i.e., the delta between start and current n
        """
        elapsed = clamp(elapsed, 0, self.total)
        increment = elapsed - self.n
        self.update(increment)


def clamp(val, vmin, vmax):
    val = max(val, vmin)
    val = min(val, vmax)
    return val



def tqdm_sleep(seconds, ndiv=100):
    delta = seconds / float(ndiv)
    for _ in tqdm.trange(ndiv):
        sleep(delta)



