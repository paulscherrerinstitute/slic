from slic.core.device import Device
from slic.devices.general.adjustable import AdjustableVirtual
from slic.devices.general.delay_stage import DelayStage
from slic.devices.general.motor import Motor
from slic.devices.general.smaract import SmarActAxis

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



class ExpLaser(Device):

    def __init__(self, ID, name="Laser motor positions", ID_SA="SARES23", smar_config=None, **kwargs):
        super().__init__(ID, name=name, **kwargs)
        self.ID_SA = ID_SA
        self.smar_config = smar_config

        # Waveplate and Delay stage
        self.pump_wp = Motor(ID + "-M534:MOT")
        self.tt_wp = Motor(ID + "-M533:MOT")

        self.pump_delay_stg = Motor(ID + "-M521:MOTOR_1")
        self.pump_delay = DelayStage(self.pump_delay_stg)

        self.delay_eos_stg = Motor(ID + "-M521:MOTOR_1")
        self.delay_eos = DelayTime(self.delay_eos_stg, name="delay_eos")
        self.lxt_eos = DelayTime(self.delay_eos_stg, direction=-1, name="lxt_eos")

        self.delay_tt_stg = Motor(ID + "-M522:MOTOR_1")
        self.delay_tt = DelayTime(self.delay_tt_stg, name="delay_tt")

        self.delay_glob_stg = Motor(ID + "-M523:MOTOR_1")
        self.delay_glob = DelayTime(self.delay_glob_stg, name="delay_glob")
        self.lxt_glob = DelayTime(self.delay_glob_stg, direction=-1, name="lxt_glob")

        self.delay_lxtt = DelayCompensation([self.delay_glob, self.delay_tt], [-1, 1], name="delay_lxtt")

        self.compressor = Motor(ID + "-M532:MOT")

        self.lam_delay_smar_stg = SmarActAxis("SLAAR21-LMTS-LAM11")
        self.lam_delay_smar = DelayStage(self.lam_delay_smar_stg)

        self.lam_delay_stg = Motor(ID + "-M548:MOT")
        self.lam_delay = DelayStage(self.lam_delay_stg)

        self.palm_delay_stg = Motor(ID + "-M552:MOT")
        self.palm_delay = DelayStage(self.palm_delay_stg)

        self.psen_delay_stg = Motor(ID + "-M561:MOT")
        self.psen_delay = DelayStage(self.psen_delay_stg)

        # Mirrors used in the experiment
        for smar_name, smar_address in self.smar_config.items():
            sa = SmarActAxis(ID_SA + smar_address)
            setattr(self, sa, smar_name)



