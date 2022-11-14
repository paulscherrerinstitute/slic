from slic.core.adjustable import PVAdjustable
from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor
from slic.devices.general.delay_stage import DelayStage, Delay
from slic.devices.general.smaract import SmarActAxis
from slic.devices.timing.lasertiming import ETiming, LXTPumpProbe


class ExpLaser(Device):

    def __init__(self):
        ID = "SLAAR11-LMOT"
        super().__init__(ID, "Experiment laser hardware", "Laser motor positions", 122)

        # Laser repetition rate
        self.repRate = PVAdjustable("SIN-TIMAST-TMA:Evt-20-Freq-I")
        self.darkRate = PVAdjustable("SIN-TIMAST-TMA:Evt-23-Freq-I")

        # Waveplates
        self.wpTopas = Motor(ID + "-M442:MOT")
        self.wpHarmonics = Motor(ID + "-M432:MOT")

        # Delay stages
        self.pumpTopas_delay = DelayStage(ID + "-M451:MOTOR_1", "Delay Pump Topas")
        self.pumpHarmonics_delay = DelayStage(ID + "-M453:MOTOR_1", "Delay Pump Harmonics")
        self.globalglobi_delay = DelayStage(ID + "-M452:MOTOR_1", "Delay Global Globi")

        # PALM delay stages
        self.palm_delay = DelayStage(ID + "-M423:MOT")
        self.palmEO_delay = DelayStage(ID + "-M422:MOT")

        # PSEN delay stage
        self.psen_delay = DelayStage(ID + "-M424:MOT")

        # Experimental compressor delay stage
        self.compressorExp_delay = Motor(ID + "-M431:MOT")

        # Experimental compressor delay stage
        self.compressorDiag_delay = Motor(ID + "-M421:MOT")

        # variable OD filter
        self.vODfilter = Motor(ID + "-M444:MOT", "Variable OD Filter")

        # Experiment-FEL timing delay stage
        self.pump_toFEL_delay = DelayStage(ID + "-M441:MOT")

        # Experiment focussing lens position
        self.pump_lens_focus = Motor(ID + "-M443:MOT")

        # Globi electronic timing PV from Edwin
        self.eTiming = ETiming(ID + "-eTiming")
        self.lxt_pp = LXTPumpProbe("SLAAR01-LTIM-PDLY:DELAYNS", pvname_done_moving="SLAAR01-LTIM-PDLY:WAITING")

        # FROG
        frog_motor = SmarActAxis("SLAAR11-LMTS-FROG1")
        frog_delay = Delay(frog_motor)
        self.FROG = SimpleDevice("FROG",
            motor = frog_motor,
            delay = frog_delay
        )



