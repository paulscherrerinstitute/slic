import numpy as np
from scipy import constants
import xraylib as xl


def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:, 0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m, 1:])
        for j in range(1, arrays[0].size):
            out[j * m : (j + 1) * m, 1:] = out[0:m, 1:]
    return out


def E2lam(energy):
    """energy in eV, lambda in Ångstrøm"""
    return constants.h * constants.c / constants.e / energy * 1e10


def QE2theta(Q, energy):
    """Q in Å**(-1), energy in eV, theta in radians"""
    return np.arcsin(E2lam(energy) / 4 / np.pi * Q)


def absorptionEdge(element, edge=None):
    if type(element) is str:
        element = xl.SymbolToAtomicNumber(element)
    shells = ["K", "L1", "L2", "L3", "M1", "M2", "M3", "M4", "M5"]
    if edge is not None:
        shell_ind = shells.index(edge)
        return xl.EdgeEnergy(element, shell_ind)
    else:
        shell_inds = range(8)
        print("Absorption edges %s" % xl.AtomicNumberToSymbol(element))
        for shell_ind in shell_inds:
            print(
                "  "
                + shells[shell_ind].ljust(3)
                + " = %7.1f eV" % (xl.EdgeEnergy(element, shell_ind) * 1000)
            )
