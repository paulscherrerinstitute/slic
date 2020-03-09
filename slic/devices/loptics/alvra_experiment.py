from slic.controls.pv import PV
from slic.utils.printing import format_header, printable_dict

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
        self.pumpTopas_delay = DelayStage(Id + "-M451:MOTOR_1")
        self.pumpHarmonics_delay = DelayStage(Id + "-M453:MOTOR_1")
        self.globalglobi_delay = DelayStage(Id + "-M452:MOTOR_1")

        # PALM delay stages
        self.palm_delay = DelayStage(Id + "-M423:MOT")
        self.palmEO_delay = DelayStage(Id + "-M422:MOT")

        # PSEN delay stage
        self.psen_delay = DelayStage(Id + "-M424:MOT")

        # Experimental compressor delay stage
        self.compressorExp_delay = MotorRecord(Id + "-M431:MOT")

        # Experimental compressor delay stage
        self.compressorDiag_delay = MotorRecord(Id + "-M421:MOT")

        # Pump A/C delay stage
        self.pump_autocorr_delay = DelayStage(Id + "-M444:MOT")

        # Experiment-FEL timing delay stage
        self.pump_toFEL_delay = DelayStage(Id + "-M441:MOT")

        # Experiment focussing lens position
        self.pump_lens_focus = MotorRecord(Id + "-M443:MOT")

        # Globi electronic timing PV from Edwin
        self.eTiming = eTiming(Id + "-eTiming")


    def __repr__(self):
        head = "Laser motor positions"
        head = format_header(head)

        to_print = {}
        for key, item in self.__dict__.items():
            if type(item) in [MotorRecord, DelayStage, PV, eTiming]:
                to_print[key] = item

        to_print = printable_dict(to_print)
        return head + "\n" + to_print



