import xrayutilities as xu
from . import consts as _consts
from scipy.constants import torr, bar, k, N_A, R
import numpy as np

# This module holds relevant materials of the
# xrayutilities materials class,


class MaterialCollection:
    """ Dummy class collections of materials (dict-like)."""

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __setitem__(self, key, value):
        self.__dict__.update({key: value})


_amorphous = dict()
_crystal = dict()
_gas = dict()

amorphous = MaterialCollection()
crystal = MaterialCollection()
gas = MaterialCollection()


def _get_transmission(self, d, E="config"):
    """ calculate the transmittion after thickness d (in m) of material at energy E (in eV)."""
    return np.exp(-d * 1e6 / self.absorption_length(E))


xu.materials.Material.transmission = _get_transmission


crystal["Si"] = xu.materials.Si
crystal["Ge"] = xu.materials.Ge
crystal["GaAs"] = xu.materials.GaAs
crystal["Al"] = xu.materials.Al
crystal["Diamond"] = xu.materials.C
crystal["Be"] = xu.materials.material.Crystal(
    "Be",
    xu.materials.spacegrouplattice.SGLattice(
        194, 2.2858, 3.5843, atoms=[xu.materials.elements.Be], pos=["2c"]
    ),
)

amorphous["B4C"] = xu.materials.material.Amorphous("B4C", 2520, [("B", 4), ("C", 1)])
amorphous["Mo"] = xu.materials.material.Amorphous("Mo", 10220, [("Mo", 1)])
amorphous["polyimide"] = xu.materials.material.Amorphous(
    "polyimide", 1430, [("C", 22), ("H", 10), ("N", 2), ("O", 5)]
)
amorphous["mylar"] = xu.materials.material.Amorphous(
    "mylar", 1400, [("C", 10), ("H", 8), ("O", 4)]
)
amorphous["polycarbonate"] = xu.materials.material.Amorphous(
    "polycarbonate", 1200, [("C", 16), ("H", 14), ("O", 3)]
)
amorphous["Si3N4"] = xu.materials.material.Amorphous(
    "Silicon nitride", 3440, [("Si", 3), ("N", 4)]
)
amorphous["air"] = xu.materials.material.Amorphous(
    "air", 1000, [("N", 1.562), ("O", 0.42), ("C", 0.0003), ("Ar", 0.0094)]
)


# more useful values and constants
# elementName = DummyClassDict(_consts.elementName)
# meltPoint = DummyClassDict(_consts.meltPoint)
# density = DummyClassDict(_consts.Density)


class Gas(xu.materials.material.Amorphous):
    def __init__(
        self, name, pressure=bar, temperature=295, molecule_size=1, atoms=None, cij=None
    ):
        """pressure in Pascal, temperature in Kelvin"""
        self.pressure = pressure
        self.temperature = temperature
        self.molecule_size = molecule_size
        super(Gas, self).__init__(name, 0, atoms=atoms, cij=cij)

    def _getdensity(self):
        """
        calculates the mass density of an material from the atomic composition and the average molecule size (ideal gas).

        Returns
        -------
        mass density in kg/m^3
        """
        num_dens = self.pressure / k / self.temperature
        return self._get_composition_mass() * num_dens * self.molecule_size

    density = property(_getdensity)

    def _get_composition_mass(self):
        w = 0
        for atom, occ in self.base:
            w += atom.weight * occ
        return w


gas["air"] = Gas(
    "air",
    molecule_size=1.9917,
    atoms=[("N", 1.562), ("O", 0.42), ("C", 0.0003), ("Ar", 0.0094)],
)
gas["He"] = Gas("He", molecule_size=1, atoms=[("He", 1)])
gas["N"] = Gas("He", molecule_size=2, atoms=[("N", 1)])
