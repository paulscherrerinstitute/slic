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

        # Experiment table delay stages
        #pump_topas  = DelayStage(ID + "-M451:MOTOR_1", "Delay Pump Topas")
        timetool    = DelayStage(ID + "-M453:MOTOR_1", name="laser.motion.timetool")
        globalglobi = DelayStage(ID + "-M452:MOTOR_1", name="laser.motion.globalglobi")
        pumpprobex = PVAdjustable("SLAAR11-LMOT-OWIS1_4:DRIVE", pvname_readback="SLAAR11-LMOT-OWIS1_4:MOTRBV", pvname_moving="SLAAR11-LMOT-OWIS1_4:MOVINGS", wait_time=3)
        pumpprobet = PVAdjustable("SLAAR01-LTIM-PDLY-M1:SYS_MOVE_TO", pvname_readback='SLAAR11-L-BECKBS:PR1_CH4_VAL_GET', pvname_moving="SLAAR11-LMOT-OWIS1_4:MOVINGS", name="laser.delay.pumpprobe")

        # Optical transient absorption delay stages
        ota_compensation = DelayStage(ID + "-M424:MOT", name="laser.motion.ota_compensation")
        ota_pp = DelayStage(ID + "-M451:MOTOR_1", name="laser.motion.ota_pp")

        # Compressor delay stage
        compressor_exp  = Motor(ID + "-M431:MOT", name="laser.motion.compressor_exp")
        compressor_diag = Motor(ID + "-M421:MOT", name="laser.motion.compressor_diag")

        # rotation stages
        wp_compressor = Motor(ID + "-M432:MOT", name="laser.rotate.wp_compressor")
        wp_experiment = PVAdjustable("SLAAR11-LMOT-ELL3:DRIVE", name="laser.rotate.wp_experiment", pvname_moving="SLAAR11-LMOT-ELL3:MOVING.RVAL")
        #wp_topas      = Motor(ID + "-M442:MOT")
        vOD_whitelight = PVAdjustable("SLAAR11-LMOT-ELL1:DRIVE", name="laser.rotate.vOD_whitelight", pvname_moving="SLAAR11-LMOT-ELL1:MOVING.RVAL")
        vOD_experiment = PVAdjustable("SLAAR11-LMOT-ELL2:DRIVE", name="laser.rotate.vOD_experiment", pvname_moving="SLAAR11-LMOT-ELL2:MOVING.RVAL")
        vOD_filter     = Motor(ID + "-M444:MOT", name="laser.rotate.vOD_filter_depr")

        # Globi electronic timing PV from Edwin
        eTiming  = ETiming(ID + "-eTiming")
        lxtpp    = LXTPumpProbe("SLAAR01-LTIM-PDLY:DELAYNS", pvname_done_moving="SLAAR01-LTIM-PDLY:WAITING", name="laser.delay.lxt")
        #lxtpp_ns = LXTPumpProbe("SLAAR03-LTIM-PDLY:DELAYNS_SLOW", name="OPO Pump Probe")

        # FROG
        frog_motor = SmarActAxis("SLAAR11-LMTS-FROG11")
        frog_delay = Delay(frog_motor)


        # SimpleDevices to classify Adjustables (can probably be automatic)

        self.motion = SimpleDevice("Motion",
            #wp_topas = wp_topas,
            wp_compressor = wp_compressor,
            wp_experiment = wp_experiment,
            vOD_filter = vOD_filter,
            vOD_whitelight = vOD_whitelight,
            vOD_experiment = vOD_experiment,

            compressor_exp = compressor_exp,
            compressor_diag = compressor_diag,

            #pump_topas = pump_topas.motor,
            #xraypp = xraypp,
            pumpprobe = pumpprobex,
            timetool = timetool.motor,
            globalglobi = globalglobi.motor,

            frog = frog_motor,

            ota_compensation = ota_compensation.motor,
            ota_pp = ota_pp.motor
        )

        self.delay = SimpleDevice("Delay",
            eTiming = eTiming,
            lxtpp = lxtpp,
            #lxtpp_ns = lxtpp_ns,

            #xraypp = xraypp_delay,
            pumpprobe = pumpprobet,
            timetool = timetool.delay,
            globalglobi = globalglobi.delay,

            frog = frog_delay,

            ota_compensation = ota_compensation.delay,
            ota_pp = ota_pp.delay
        )



