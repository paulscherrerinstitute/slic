from epics import PV

from ..basedevice import BaseDevice
from ..general.motors import MotorRecord
from ..general.delay_stage import DelayStage
from ..timing.alvralasertiming import eTiming


class LaserExp(BaseDevice):
    """Experiment laser hardware"""

    def __init__(self):
        self.Id = Id = "SLAAR11-LMOT"
        self.z_undulator = 122

        # Laser repetition rate
        self.repRate = PV("SIN-TIMAST-TMA:Evt-20-Freq-I")
        self.darkRate = PV("SIN-TIMAST-TMA:Evt-23-Freq-I")

        # Waveplates
        self.wpTopas = MotorRecord(Id + "-M442:MOT")
        self.wpHarmonics = MotorRecord(Id + "-M432:MOT")

        # Delay stages
        self.pumpTopas_delay = MotorRecord(Id + "-M451:MOTOR_1")
        self.pumpTopas_delayTime = DelayStage(self.pumpTopas_delay)

        self.pumpHarmonics_delay = MotorRecord(Id + "-M453:MOTOR_1")
        self.pumpHarmonics_delayTime = DelayStage(self.pumpHarmonics_delay)

        self.globalglobi_delay = MotorRecord(Id + "-M452:MOTOR_1")
        self.globalglobi_delayTime = DelayStage(self.globalglobi_delay)

        # PALM delay stages
        self.palm_delay = MotorRecord(Id + "-M423:MOT")
        self.palm_delayTime = DelayStage(self.palm_delay)

        self.palmEO_delay = MotorRecord(Id + "-M422:MOT")
        self.palmEO_delayTime = DelayStage(self.palmEO_delay)

        # PSEN delay stage
        self.psen_delay = MotorRecord(Id + "-M424:MOT")
        self.psen_delayTime = DelayStage(self.psen_delay)

        # Experimental compressor delay stage
        self.compressorExp_delay = MotorRecord(Id + "-M431:MOT")

        # Experimental compressor delay stage
        self.compressorDiag_delay = MotorRecord(Id + "-M421:MOT")

        # Pump A/C delay stage
        self.pump_autocorr_delay = MotorRecord(Id + "-M444:MOT")
        self.psen_autocorr_delayTime = DelayStage(self.pump_autocorr_delay) #TODO: looks like a typo

        # Experiment-FEL timing delay stage
        self.pump_toFEL_delay = MotorRecord(Id + "-M441:MOT")
        self.pump_toFEL_delayTime = DelayStage(self.pump_toFEL_delay)

        # Experiment focussing lens position
        self.pump_lens_focus = MotorRecord(Id + "-M443:MOT")

        # Globi electronic timing PV from Edwin
        self.eTiming = eTiming(Id + "-eTiming")


    def __repr__(self):
        ostr = "Laser motor positions\n"

        res = {}
        for key, item in self.__dict__.items():
            if hasattr(item,"get_current_value"):
                pos = item.get_current_value()
            elif hasattr(item,"get"):
                pos = item.get()
            else:
                continue
            res[key] = pos

        length = max(len(k) for k in res) + 1
        lines = sorted("{}:{}{}".format(k, " "*(length-len(k)), v) for k, v in res.items())
        ostr += "\n".join(lines)
        return ostr



