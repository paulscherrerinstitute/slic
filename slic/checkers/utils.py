
def within(val, vmin, vmax):
    vmin, vmax = sorted(vmin, vmax)
    left  = True if vmin is None else (vmin <= val) #TODO: equal?
    right = True if vmax is None else (val < vmax) #TODO: equal?
    return (left & right) # & works for regular Python numbers and numpy arrays


def within_fraction(data, vmin, vmax):
    data = np.asarray(data)
    good = within(data, vmin, vmax)

    ntotal = len(data)
    ngood  = sum(good)

    fraction = ngood / ntotal
    return fraction


def fraction_to_percentage(fraction, ndigits=1):
    percentage = fraction * 100
    percentage = round(percentage, ndigits)
    return percentage



