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
        self.rates = SimpleDevice("Rate",
            rep_rate  = PVAdjustable("SIN-TIMAST-TMA:Evt-20-Freq-I"),
            dark_rate = PVAdjustable("SIN-TIMAST-TMA:Evt-23-Freq-I")
        )

        # Waveplates
        wp_topas     = Motor(ID + "-M442:MOT")
        wp_harmonics = Motor(ID + "-M432:MOT")

        # Delay stages
        pump_topas  = DelayStage(ID + "-M451:MOTOR_1", "Delay Pump Topas")
        pumpprobe   = DelayStage(ID + "-M451:MOTOR_1", "Delay Pump Probe")
        timetool    = DelayStage(ID + "-M453:MOTOR_1", "Delay Time Tool")
        globalglobi = DelayStage(ID + "-M452:MOTOR_1", "Delay Global Globi")

        # PALM delay stages
#        palm   = DelayStage(ID + "-M423:MOT")
#        palmEO = DelayStage(ID + "-M422:MOT")

        # PSEN delay stage
#        psen = DelayStage(ID + "-M424:MOT")

        # Compressor delay stage
        compressor_exp  = Motor(ID + "-M431:MOT", "Compressor Experiment")
        compressor_diag = Motor(ID + "-M421:MOT", "Compressor Diagnostics")

        # variable OD filter
        vODfilter = Motor(ID + "-M444:MOT", name="Variable OD Filter")

        # Experiment-FEL timing delay stage
#        toFEL = DelayStage(ID + "-M441:MOT")

        # Experiment focussing lens position
#        lens_focus = Motor(ID + "-M443:MOT")

        # Globi electronic timing PV from Edwin
        eTiming = ETiming(ID + "-eTiming")
        lxtpp = LXTPumpProbe("SLAAR01-LTIM-PDLY:DELAYNS", pvname_done_moving="SLAAR01-LTIM-PDLY:WAITING", name="LXT Pump Probe")

        # FROG
        frog_motor = SmarActAxis("SLAAR11-LMTS-FROG1")
        frog_delay = Delay(frog_motor)


        # SimpleDevices to classify Adjustables (can probably be automatic)

        self.motion = SimpleDevice("Motion",
            wp_topas = wp_topas,
            wp_harmonics = wp_harmonics,
            compressor_exp = compressor_exp,
            compressor_diag = compressor_diag,
            vODfilter = vODfilter,

            pump_topas = pump_topas.motor,
            pumpprobe = pumpprobe.motor,
            timetool = timetool.motor,
            globalglobi = globalglobi.motor,

            frog = frog_motor
        )

        self.delay = SimpleDevice("Delay",
            eTiming = eTiming,
            lxtpp = lxtpp,

            pump_topas = pump_topas.delay,
            pumpprobe = pumpprobe.delay,
            timetool = timetool.delay,
            globalglobi = globalglobi.delay,

            frog = frog_delay
        )



