import numpy as np


def within(val, vmin, vmax):
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



