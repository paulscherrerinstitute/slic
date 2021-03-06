from slic.core.adjustable import PVAdjustable
from slic.devices.general.motor import Motor
from ..device import Device
from ..general.delay_stage import DelayStage
from ..timing.lasertiming import ETiming


class LaserExp(Device):

    def __init__(self):
        Id = "SLAAR11-LMOT"
        super().__init__(Id, "Experiment laser hardware", "Laser motor positions", 122)

        # Laser repetition rate
        self.repRate = PVAdjustable("SIN-TIMAST-TMA:Evt-20-Freq-I")
        self.darkRate = PVAdjustable("SIN-TIMAST-TMA:Evt-23-Freq-I")

        # Waveplates
        self.wpTopas = Motor(Id + "-M442:MOT")
        self.wpHarmonics = Motor(Id + "-M432:MOT")

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
        self.compressorExp_delay = Motor(Id + "-M431:MOT")

        # Experimental compressor delay stage
        self.compressorDiag_delay = Motor(Id + "-M421:MOT")

        # Pump A/C delay stage
#        self.pump_autocorr_delay = DelayStage(Id + "-M444:MOT")
        self.pump_autocorr_delay = Motor(Id + "-M444:MOT")

        # Experiment-FEL timing delay stage
        self.pump_toFEL_delay = DelayStage(Id + "-M441:MOT")

        # Experiment focussing lens position
        self.pump_lens_focus = Motor(Id + "-M443:MOT")

        # Globi electronic timing PV from Edwin
        self.eTiming = ETiming(Id + "-eTiming")



