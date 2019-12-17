import numpy as np
from matplotlib import pylab as plt


def readTraceTextfile(fina, numbers=None):
    if not numbers is None:
        d = [readTraceTextfile(fina % number) for number in numbers]
    else:
        d = np.loadtxt(fina, skiprows=5, delimiter=",")
    return d


def getRiseTime(t, s, lims=[0.1, 0.9]):
    lims = np.asarray(lims)
    t = np.asarray(t)
    s = np.asarray(s)
    sel = t > 0
    mxind = np.min((np.diff(s[sel]) < 0).nonzero()[0])
    mxind = sel.nonzero()[0][mxind]
    sel = t <= 0
    mnind = np.max((np.diff(s[sel]) < 0).nonzero()[0])
    mnind = sel.nonzero()[0][mnind] + 1
    crosspty = lims * (s[mxind] - s[mnind]) + s[mnind]
    crossptx = np.interp(crosspty, s[mnind : mxind + 1], t[mnind : mxind + 1])
    return float(np.round(np.diff(crossptx), decimals=13)), [crossptx, crosspty]


def plotTrace(fina="./scope2_testdata_2017-02-21/C2Trace00003txt"):
    t, s = readTraceTextfile(fina).T
    rt, crossers = getRiseTime(t, s)
    ax = plt.gca()
    ax.plot(t, s, ".-", label="rise time = %3g (fwhm)" % rt)
    ax.plot(crossers[0], crossers[1], "xr")
    ax.set_xlabel("Time / s")
    ax.set_ylabel("Amplitude / V")
