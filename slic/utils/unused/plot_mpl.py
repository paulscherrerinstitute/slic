import matplotlib.pyplot as plt


def identifyContrastplotData(x, y, i):
    assert i.ndim == 2, "Intensity data needs to be 2 dimensional!"
    assert (
        x.ndim == y.ndim
    ), "please provide x and y plotting coordinate in same dimension"
