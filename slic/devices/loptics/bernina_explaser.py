from slic.core.device import Device
from slic.devices.general.delay_compensation import DelayCompensation
from slic.devices.general.delay_stage import DelayStage
from slic.devices.general.delay_time import DelayTime
from slic.devices.general.motor import Motor
from slic.devices.general.smaract import SmarActAxis


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



