from slic.devices.general.motor import Motor
from ..general.smaract import SmarActAxis
from ..general.delay_stage import DelayStage
from ..general.adjustable import AdjustableVirtual

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
    """Simple virtual adjustable for compensating delay adjustables. It assumes the first adjustable is the master for 
    getting the current value."""

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



class ExpLaser:

    def __init__(self, ID=None, name=None, smar_config=None):
        self.ID = ID
        self.ID_Exp1 = "SARES20-EXP"
        self.ID_SA = "SARES23"
        self.name = name
        self.smar_config = smar_config

        # Waveplate and Delay stage
        self.pump_wp = Motor(ID + "-M534:MOT")
        self.tt_wp = Motor(ID + "-M533:MOT")

        self._pump_delaystg = Motor(ID + "-M521:MOTOR_1")
        self.pump_delay = DelayStage(self._pump_delaystg)

        self.delay_eos_stg = Motor(ID + "-M521:MOTOR_1")
        self.delay_eos = DelayTime(self.delay_eos_stg, name="delay_eos")
        self.lxt_eos = DelayTime(self.delay_eos_stg, direction=-1, name="lxt_eos")

        self.delay_tt_stg = Motor(ID + "-M522:MOTOR_1")
        self.delay_tt = DelayTime(self.delay_tt_stg, name="delay_tt")

        self.delay_glob_stg = Motor(ID + "-M523:MOTOR_1")
        self.delay_glob = DelayTime(self.delay_glob_stg, name="delay_glob")
        self.lxt_glob = DelayTime(self.delay_glob_stg, direction=-1, name="lxt_glob")

        # Implementation of delay compensation, this assumes for now that delays_glob and delay_tt actually delay in positive directions.
        self.delay_lxtt = DelayCompensation([self.delay_glob, self.delay_tt], [-1, 1], name="delay_lxtt")

        # compressor
        self.compressor = Motor(ID + "-M532:MOT")
#        self.compressor = Motor(ID + '-M532:MOT')

        # LAM delay stages
        self._lam_delay_smarstg = SmarActAxis("SLAAR21-LMTS-LAM11")
        self.lam_delay_smar = DelayStage(self._lam_delay_smarstg)
#        self._lam_delayStg_Smar = SmarActAxis('SLAAR21-LMTS-LAM11')
#        self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        self._lam_delaystg = Motor(ID + "-M548:MOT")
        self.lam_delay = DelayStage(self._lam_delaystg)
#        self._lam_delayStg = Motor(ID + '-M548:MOT')
#        self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        self._palm_delaystg = Motor(ID + "-M552:MOT")
        self.palm_delay = DelayStage(self._palm_delaystg)
#        self._palm_delayStg = Motor(ID + '-M552:MOT')
#        self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
#        self._psen_delayStg = Motor(ID + '')
#        self.psen_delay = DelayStage(self._pump_delayStg)
        self._psen_delaystg = Motor(ID + "-M561:MOT")
        self.psen_delay = DelayStage(self._psen_delaystg)

        # SmarActID
        # Mirrors used in the experiment
        for smar_name, smar_address in self.smar_config.items():
            sa = SmarActAxis(self.ID_SA + smar_address)
            setattr(self, sa, smar_name)


    def __repr__(self):
        ostr = "*****Laser motor positions******\n"
        for tkey, item in sorted(self.__dict__.items()):
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                posdialstr = ""
                try:
                    posdial = item.get_current_value(postype="dial")
                    posdialstr = "    dial:  % 14g\n" % posdial
                except:
                    pass
                ostr += "  " + tkey.ljust(18) + " : % 14g\n" % pos + posdialstr
        return ostr



class Laser_Exp_old:

    def __init__(self, ID=None, name=None, smar_config=None):
        self.ID = ID
        self.ID_Exp1 = "SARES20-EXP"
        self.ID_SA = "SARES23"
        self.name = name
        self.smar_config = smar_config

        # Waveplate and Delay stage
        self.pump_wp = Motor(ID + "-M534:MOT")
        self.tt_wp = Motor(ID + "-M533:MOT")

        self._pump_delaystg = Motor(ID + "-M521:MOTOR_1")
        self.pump_delay = DelayStage(self._pump_delaystg)

        self._tt_delaystg = Motor(ID + "-M522:MOTOR_1")
        self.tt_delay = DelayStage(self._tt_delaystg)
#        self.thz_delay = DelayStage(self._thz_delaystg)

        self._exp_delaystg = Motor(ID + "-M553:MOT")
        self.exp_delay = DelayStage(self._exp_delaystg)
#        self.thz_delay = DelayStage(self._thz_delaystg)

        # compressor
        self.compressor = Motor(ID + "-M532:MOT")
#        self.compressor = Motor(ID + '-M532:MOT')

        # LAM delay stages
        self._lam_delay_smarstg = SmarActAxis("SLAAR21-LMTS-LAM11")
        self.lam_delay_smar = DelayStage(self._lam_delay_smarstg)
#        self._lam_delayStg_Smar = SmarActAxis('SLAAR21-LMTS-LAM11')
#        self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        self._lam_delaystg = Motor(ID + "-M548:MOT")
        self.lam_delay = DelayStage(self._lam_delaystg)
#        self._lam_delayStg = Motor(ID + '-M548:MOT')
#        self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        self._palm_delaystg = Motor(ID + "-M552:MOT")
        self.palm_delay = DelayStage(self._palm_delaystg)
#        self._palm_delayStg = Motor(ID + '-M552:MOT')
#        self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
#        self._psen_delayStg = Motor(ID + '')
#        self.psen_delay = DelayStage(self._pump_delayStg)

        # SmarActID
        # Mirrors used in the experiment
        for smar_name, smar_address in self.smar_config.items():
            sa = SmarActAxis(self.ID_SA + smar_address)
            setattr(self, sa, smar_name)


    def __repr__(self):
        ostr = "*****Laser motor positions******\n"
        for tkey, item in sorted(self.__dict__.items()):
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                posdialstr = ""
                try:
                    posdial = item.get_current_value(postype="dial")
                    posdialstr = "    dial:  % 14g\n" % posdial
                except:
                    pass
                ostr += "  " + tkey.ljust(18) + " : % 14g\n" % pos + posdialstr
        return ostr



