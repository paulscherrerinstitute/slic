import xrayutilities as xu
import xraylib as xl
import numpy as np
from . import materials


def getKBMirrorLayer():
    subst = xu.simpack.Layer(materials.crystal.Si, np.inf)
    highZ = xu.simpack.Layer(materials.amorphous.Mo, 200)
    lowZ = xu.simpack.Layer(materials.amorphous.B4C, 150)
    return subst + highZ + lowZ


def calcReflectivity(
    mirror=getKBMirrorLayer(),
    energys=np.linspace(2000, 12000, 200),
    alphais=np.linspace(0, 3, 200),
    sample_width=500,
    **kwargs
):
    Refl = []
    for E in energys:
        m = xu.simpack.SpecularReflectivityModel(mirror, energy=E, **kwargs)
        Refl.append(m.simulate(alphais))

    return np.asarray(Refl), energys, alphais


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
