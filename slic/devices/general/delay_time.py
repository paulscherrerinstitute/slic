from slic.devices.general.adjustable import AdjustableVirtual

import colorama, datetime
from pint import UnitRegistry

ureg = UnitRegistry()


class DelayTime(AdjustableVirtual):

    def __init__(self, stage, direction=1, passes=2, reset_current_value_to=True, name=None):
        self._direction = direction
        self._group_velo = 299798458  # m/s
        self._passes = passes
        self.ID = stage.ID + "_delay"
        self._stage = stage
        AdjustableVirtual.__init__(
            self, [stage], self._mm_to_s, self._s_to_mm, reset_current_value_to=reset_current_value_to, name=name,
        )

    def _mm_to_s(self, mm):
        return mm * 1e-3 * self._passes / self._group_velo * self._direction

    def _s_to_mm(self, s):
        return s * self._group_velo * 1e3 / self._passes * self._direction

    def __repr__(self):
        s = ""
        s += f"{colorama.Style.DIM}"
        s += datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ": "
        s += f"{colorama.Style.RESET_ALL}"
        s += f"{colorama.Style.BRIGHT}{self._get_name()}{colorama.Style.RESET_ALL} at "
        s += f"{(self.get_current_value()*ureg.second).to_compact():P~6.3f}"
        s += f"{colorama.Style.RESET_ALL}"
        return s

    def get_limits(self):
        return [self._mm_to_s(tl) for tl in self._stage.get_limits()]

    def set_epics_limits(self, low_limit, high_limit):
        lims_stage = [self._s_to_mm(tl) for tl in [low_limit, high_limit]]
        lims_stage.sort()
        self._stage.set_epics_limits(*lims_stage)

        return [self._mm_to_s(tl) for tl in self._stage.get_limits()]



