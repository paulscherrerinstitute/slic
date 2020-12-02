import numpy as np

from .utils import iround


def nice_arange(start, stop, step=1, **kwargs):
    start, stop, step = normalize_direction(start, stop, step)

    delta = stop - start
    num = delta / step
    num = int(round(np.abs(num)))

    return nice_linspace(start, stop, num, **kwargs)


def nice_linspace(start, stop, num, **kwargs):
    return np.linspace(start, stop, num + 1, **kwargs)


def nice_steps_centered(start, stop, step=1, endpoint=True, **kwargs):
    start, stop, step = normalize_direction(start, stop, step)

    istart = istep(start, step)
    istop  = istep(stop, step)

    if endpoint:
        istop += 1

    return step * np.arange(istart, istop, **kwargs)


def nice_steps_left_aligned(start, stop, step=1, endpoint=True, **kwargs):
    start, stop, step = normalize_direction(start, stop, step)

    delta = stop - start
    idelta = istep(delta, step)

    if endpoint:
        idelta += 1

    return start + step * np.arange(idelta, **kwargs)


def nice_steps_right_aligned(start, stop, step=1, endpoint=True, **kwargs):
    start, stop, step = normalize_direction(start, stop, step)

    delta = stop - start
    idelta = istep(delta, step)

    if endpoint:
        idelta += 1

    steps = stop - step * np.arange(idelta, **kwargs)
    return steps[::-1]


def normalize_direction(start, stop, step):
    sign = np.sign(step)
    step = np.abs(step)

    if sign == -1:
        start, stop = stop, start

    if start > stop:
        step *= -1

    return start, stop, step


def istep(val, step):
    return iround(val / step)



def within(val, vmin, vmax):
    if vmin is not None and vmax is not None:
        vmin, vmax = sorted((vmin, vmax))
    left  = True if vmin is None else (vmin <= val) #TODO: equal?
    right = True if vmax is None else (val < vmax)  #TODO: equal?
    return (left & right) # & works for regular Python booleans and numpy arrays


def within_fraction(data, vmin, vmax):
    data = np.asarray(data)
    good = within(data, vmin, vmax)

    ntotal = len(data)
    ngood  = sum(good)

    if not ntotal:
        return 0

    fraction = ngood / ntotal
    return fraction


def fraction_to_percentage(fraction, ndigits=1):
    percentage = fraction * 100
    percentage = round(percentage, ndigits)
    return percentage


def get_dtype(v):
    if is_array(v):
        return v.dtype
    else:
        return type(v)

def get_shape(v):
    if is_array(v):
        return v.shape
    else:
        return tuple()

def is_array(v):
    return isinstance(v, np.ndarray)



