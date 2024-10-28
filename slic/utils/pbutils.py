from time import sleep

from .pbar import pbar


def pbsleep(seconds, description="Waiting...", ndiv=100):
    delta = seconds / float(ndiv)
    for _ in pbrange(ndiv, description=description):
        sleep(delta)

def pbrange(*args, description=""):
    return pbar(range(*args), description=description)


