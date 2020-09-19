from slic.utils.pv import PV
from slic.utils.printing import printable_dict

from slic.devices.general.motor import Motor
from ..basedevice import BaseDevice
from ..general.delay_stage import DelayStage
from ..timing.lasertiming import ETiming


class LaserExp(BaseDevice):
    """Experiment laser hardware"""

    def __init__(self):
        self.Id = Id = "SLAAR11-LMOT"
        self.z_undulator = 122

        # Laser repetition rate
        self.repRate = PV("SIN-TIMAST-TMA:Evt-20-Freq-I")
        self.darkRate = PV("SIN-TIMAST-TMA:Evt-23-Freq-I")

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

    def __repr__(self):
        to_print = {}
        for key, item in self.__dict__.items():
            if type(item) not in (Motor, DelayStage, PV, ETiming):
                continue

            #TODO: clean up
            def get_value(dev):
                val = dev.get()
                units = dev.units
                return f"{val} {units}"

            if isinstance(item, DelayStage):
                motor = get_value(item.motor)
                delay = get_value(item.delay)
                val = " | ".join((motor, delay))
            else:
                val = get_value(item)

            to_print[key] = val

        head = "Laser motor positions"
        return printable_dict(to_print, head)



