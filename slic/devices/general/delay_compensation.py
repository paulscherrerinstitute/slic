from slic.devices.general.adjustable import AdjustableVirtual

import colorama, datetime
from pint import UnitRegistry

ureg = UnitRegistry()


class DelayCompensation(AdjustableVirtual):
    """
    Virtual adjustable for compensating delay adjustables.
    It assumes the first adjustable is the master for getting the current value.
    """

    def __init__(self, adjustables, directions, set_current_value=True, name=None):
        self._directions = directions
        self.ID = name
        AdjustableVirtual.__init__(
            self, adjustables, self._from_values, self._calc_values, set_current_value=set_current_value, name=name,
        )

    def _calc_values(self, value):
        return tuple(tdir * value for tdir in self._directions)

    def _from_values(self, *args):
        positions = [ta * tdir for ta, tdir in zip(args, self._directions)]
        return positions[0]

        tuple(tdir * value for tdir in self._directions)

    def __repr__(self):
        s = ""
        s += f"{colorama.Style.DIM}"
        s += datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ": "
        s += f"{colorama.Style.RESET_ALL}"
        s += f"{colorama.Style.BRIGHT}{self._get_name()}{colorama.Style.RESET_ALL} at "
        s += f"{(self.get_current_value()*ureg.second).to_compact():P~6.3f}"
        s += f"{colorama.Style.RESET_ALL}"
        return s



