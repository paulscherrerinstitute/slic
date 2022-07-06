from slic.utils.eco_components.aliases import Alias
from slic.devices.general.motor import Motor
from ..general.smaract import SmarActAxis
from ..general.delay_stage import DelayStage
from ..general.adjustable import AdjustableVirtual

import colorama, datetime
from pint import UnitRegistry

ureg = UnitRegistry()


def addMotorToSelf(self, ID=None, name=None):
    self.__dict__[name] = Motor(ID, name=name)
    self.alias.append(self.__dict__[name].alias)


def addSmarActAxisToSelf(self, ID=None, name=None):
    self.__dict__[name] = SmarActAxis(ID, name=name)
    self.alias.append(self.__dict__[name].alias)


def addDelayStageToSelf(self, stage=None, name=None):
    self.__dict__[name] = DelayStage(stage, name=name)
    self.alias.append(self.__dict__[name].alias)


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


class Laser_Exp:

    def __init__(self, ID=None, name=None, smar_config=None):
        self.ID = ID
        self.ID_Exp1 = "SARES20-EXP"
        self.ID_SA = "SARES23"
        self.name = name
        self.alias = Alias(name)
        self.smar_config = smar_config

        # Waveplate and Delay stage
        try:
            addMotorToSelf(self, self.ID + "-M534:MOT", name="pump_wp")
            addMotorToSelf(self, self.ID + "-M533:MOT", name="tt_wp")
        except:
            print("No wp found")

        try:
            addMotorToSelf(self, ID=self.ID + "-M521:MOTOR_1", name="_pump_delaystg")
            addDelayStageToSelf(self, stage=self.__dict__["_pump_delaystg"], name="pump_delay")
        except Exception as expt:
            print("No eos delay stage")
            print(expt)

        # try:
        addMotorToSelf(self, ID=self.ID + "-M521:MOTOR_1", name="delay_eos_stg")
        self.delay_eos = DelayTime(self.delay_eos_stg, name="delay_eos")
        self.alias.append(self.delay_eos.alias)
        self.lxt_eos = DelayTime(self.delay_eos_stg, direction=-1, name="lxt_eos")
        self.alias.append(self.lxt_eos.alias)
        # except Exception as expt:
        # print("Problems initializing eos delay stage")
        # print(expt)

        try:
            addMotorToSelf(self, ID=self.ID + "-M522:MOTOR_1", name="delay_tt_stg")
            self.delay_tt = DelayTime(self.delay_tt_stg, name="delay_tt")
            self.alias.append(self.delay_tt.alias)
        except:
            print("Problems initializing global delay stage")
        try:
            addMotorToSelf(self, ID=self.ID + "-M523:MOTOR_1", name="delay_glob_stg")
            self.delay_glob = DelayTime(self.delay_glob_stg, name="delay_glob")
            self.alias.append(self.delay_glob.alias)
            self.lxt_glob = DelayTime(self.delay_glob_stg, direction=-1, name="lxt_glob")
            self.alias.append(self.lxt_glob.alias)
        except:
            print("Problems initializing global delay stage")

        # Implementation of delay compensation, this assumes for now that delays_glob and delay_tt actually delay in positive directions.
        try:
            self.delay_lxtt = DelayCompensation([self.delay_glob, self.delay_tt], [-1, 1], name="delay_lxtt")
            self.alias.append(self.delay_lxtt.alias)
        except:
            print("Problems initializing virtual pump delay stage")
        # compressor
        addMotorToSelf(self, ID=self.ID + "-M532:MOT", name="compressor")
        # self.compressor = Motor(ID + '-M532:MOT')

        # LAM delay stages
        addSmarActAxisToSelf(self, ID="SLAAR21-LMTS-LAM11", name="_lam_delay_smarstg")
        addDelayStageToSelf(self, self.__dict__["_lam_delay_smarstg"], name="lam_delay_smar")
        # self._lam_delayStg_Smar = SmarActAxis('SLAAR21-LMTS-LAM11')
        # self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        addMotorToSelf(self, ID=self.ID + "-M548:MOT", name="_lam_delaystg")
        addDelayStageToSelf(self, self.__dict__["_lam_delaystg"], name="lam_delay")
        # self._lam_delayStg = Motor(self.ID + '-M548:MOT')
        # self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        addMotorToSelf(self, ID=self.ID + "-M552:MOT", name="_palm_delaystg")
        addDelayStageToSelf(self, self.__dict__["_palm_delaystg"], name="palm_delay")
        # self._palm_delayStg = Motor(self.ID + '-M552:MOT')
        # self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
        # self._psen_delayStg = Motor(self.ID + '')
        # self.psen_delay = DelayStage(self._pump_delayStg)
        try:
            addMotorToSelf(self, ID=self.ID + "-M561:MOT", name="_psen_delaystg")
            addDelayStageToSelf(self, stage=self.__dict__["_psen_delaystg"], name="psen_delay")
        except Exception as expt:
            print("No psen delay stage")
            print(expt)

        # SmarActID
        ### Mirrors used in the experiment ###

        for smar_name, smar_address in self.smar_config.items():
            try:
                addSmarActAxisToSelf(self, ID=(self.ID_SA + smar_address), name=smar_name)
            except:
                print("Loading %s SmarAct motor in bernina laser conifg failed") % (smar_name)

    def get_adjustable_positions_str(self):
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

    def __repr__(self):
        return self.get_adjustable_positions_str()


class Laser_Exp_old:

    def __init__(self, ID=None, name=None, smar_config=None):
        self.ID = ID
        self.ID_Exp1 = "SARES20-EXP"
        self.ID_SA = "SARES23"
        self.name = name
        self.alias = Alias(name)
        self.smar_config = smar_config

        # Waveplate and Delay stage
        try:
            addMotorToSelf(self, self.ID + "-M534:MOT", name="pump_wp")
            addMotorToSelf(self, self.ID + "-M533:MOT", name="tt_wp")
        except:
            print("No wp found")

        try:
            addMotorToSelf(self, ID=self.ID + "-M521:MOTOR_1", name="_pump_delaystg")
            addDelayStageToSelf(self, stage=self.__dict__["_pump_delaystg"], name="pump_delay")
        except:
            print("No eos delay stage")
            pass
        try:
            addMotorToSelf(self, ID=self.ID + "-M522:MOTOR_1", name="_tt_delaystg")
            addDelayStageToSelf(self, self.__dict__["_tt_delaystg"], name="tt_delay")
            # addDelayStageToSelf(self,self.__dict__["_thz_delaystg"], name="thz_delay")
        except:
            print("No thz delay stage")
            pass

        try:
            addMotorToSelf(self, ID=self.ID + "-M553:MOT", name="_exp_delaystg")
            addDelayStageToSelf(self, self.__dict__["_exp_delaystg"], name="exp_delay")
            # addDelayStageToSelf(self,self.__dict__["_thz_delaystg"], name="thz_delay")
        except:
            print("No thz delay stage")
            pass
        # compressor
        addMotorToSelf(self, ID=self.ID + "-M532:MOT", name="compressor")
        # self.compressor = Motor(ID + '-M532:MOT')

        # LAM delay stages
        addSmarActAxisToSelf(self, ID="SLAAR21-LMTS-LAM11", name="_lam_delay_smarstg")
        addDelayStageToSelf(self, self.__dict__["_lam_delay_smarstg"], name="lam_delay_smar")
        # self._lam_delayStg_Smar = SmarActAxis('SLAAR21-LMTS-LAM11')
        # self.lam_delay_Smar = DelayStage(self._lam_delayStg_Smar)

        addMotorToSelf(self, ID=self.ID + "-M548:MOT", name="_lam_delaystg")
        addDelayStageToSelf(self, self.__dict__["_lam_delaystg"], name="lam_delay")
        # self._lam_delayStg = Motor(self.ID + '-M548:MOT')
        # self.lam_delay = DelayStage(self._lam_delayStg)

        # PALM delay stages
        addMotorToSelf(self, ID=self.ID + "-M552:MOT", name="_palm_delaystg")
        addDelayStageToSelf(self, self.__dict__["_palm_delaystg"], name="palm_delay")
        # self._palm_delayStg = Motor(self.ID + '-M552:MOT')
        # self.palm_delay = DelayStage(self._palm_delayStg)

        # PSEN delay stages
        # self._psen_delayStg = Motor(self.ID + '')
        # self.psen_delay = DelayStage(self._pump_delayStg)

        # SmarActID
        ### Mirrors used in the experiment ###

        for smar_name, smar_address in self.smar_config.items():
            try:
                addSmarActAxisToSelf(self, ID=(self.ID_SA + smar_address), name=smar_name)
            except:
                print("Loading %s SmarAct motor in bernina laser conifg failed") % (smar_name)

    def get_adjustable_positions_str(self):
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

    def __repr__(self):
        return self.get_adjustable_positions_str()



