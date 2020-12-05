from types import SimpleNamespace
from time import sleep
import numpy as np
from epics import PV

from slic.core.adjustable import Adjustable, PVAdjustable, PVEnumAdjustable
from slic.devices.general.motor import Motor
from ..device import Device


class DoubleCrystalMono(Device):

    def __init__(self, Id, **kwargs):
        super().__init__(Id, **kwargs)

        self.theta  = Motor(Id + ":RX12")
        self.x      = Motor(Id + ":TX12")
        self.gap    = Motor(Id + ":T2")
        self.roll1  = Motor(Id + ":RZ1")
        self.roll2  = Motor(Id + ":RZ2")
        self.pitch2 = Motor(Id + ":RX2")

        self.energy = DoubleCrystalMonoEnergy(Id)



class DoubleCrystalMonoEnergy(Adjustable):

    def __init__(self, Id, name=None):
        pvname_setvalue = Id + ":ENERGY"
        pvname_readback = Id + ":ENERGY_SP"
        pvname_moving   = Id + ":MOVING"
        pvname_stop     = Id + ":STOP.PROC"

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback)
        pv_moving   = PV(pvname_moving)
        pv_stop     = PV(pvname_stop)

        name = name or Id
        units = pv_readback.units
        super().__init__(name=name, units=units)

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback,
            moving   = pvname_moving,
            stop     = pvname_stop
        )

        self.pvs = SimpleNamespace(
            setvalue = pv_setvalue,
            readback = pv_readback,
            moving   = pv_moving,
            stop     = pv_stop
        )


    def get_current_value(self):
        return self.pvs.readback.get()

    def set_current_value(self, value):
        self.pvs.setvalue.put(value)

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return self._as_task(changer, hold=hold, stopper=self.stop)

    def move_and_wait(self, value, wait_time=0.01, accuracy=0.5):
        self.set_current_value(value)
        while abs(self.wait_for_valid_value() - value) > accuracy:
            sleep(wait_time)

    def wait_for_valid_value(self):
        val = np.nan
        while not np.isfinite(val):
            val = self.get_current_value()
        return val

    def is_moving(self):
        done = self.pvs.moving.get()
        return not bool(done)

    def stop(self):
        self.pvs.stop.put(1)





class EcolEnergy:

    def __init__(self, Id, val="SARCL02-MBND100:P-SET", rb="SARCL02-MBND100:P-READ", dmov="SFB_BEAM_ENERGY_ECOL:SUM-ERROR-OK"):
        self.Id = Id
        self.setter = PV(val)
        self.readback = PV(rb)
        self.dmov = PV(dmov)
        self.done = False

    def get_current_value(self):
        return self.readback.get()

    def move_and_wait(self, value, wait_time=0.01, accuracy=2):
        curr = self.setter.get()
        while abs(curr - value) > 0.1:
            curr = self.setter.get()
            self.setter.put(curr + np.sign(value - curr) * 0.1)
            sleep(0.3)

        self.setter.put(value)
        while abs(self.get_current_value() - value) > accuracy:
            sleep(wait_time)
        while not self.dmov.get():
            # print(self.dmov.get())
            sleep(wait_time)

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold)



class MonoEcolEnergy:

    def __init__(self, Id):
        self.Id = Id
        self.name = "energy_collimator"
        self.dcm = DoubleCrystalMono(Id)
        self.ecol = EcolEnergy("ecol_dummy")
        self.offset = None
        self.MeVperEV = 0.78333

    def get_current_value(self):
        return self.dcm.get_current_value()

    def move_and_wait(self, value):
        ch = [self.dcm.set_target_value(value), self.ecol.set_target_value(self.calcEcol(value))]
        for tc in ch:
            tc.wait()

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold, stopper=self.dcm.stop)

    def alignOffsets(self):
        mrb = self.dcm.get_current_value()
        erb = self.ecol.get_current_value()
        self.offset = {"dcm": mrb, "ecol": erb}

    def calcEcol(self, eV):
        return (eV - self.offset["dcm"]) * self.MeVperEV + self.offset["ecol"]





class CoupledDoubleCrystalMono(Device):

    def __init__(self, Id, name="Alvra DCM coupled to FEL energy", **kwargs):
        super().__init__(Id, name=name, **kwargs)

        self.alvraMode   = PVEnumAdjustable("SAROP11-ARAMIS:MODE")
        self.FELcoupling = PVEnumAdjustable("SGE-OP2E-ARAMIS:MODE_SP")

        self.ebeamEnergy     = PVAdjustable("SARCL02-MBND100:P-READ")
        self.ebeamEnergySP   = PVAdjustable("SGE-OP2E-ARAMIS:E_ENERGY_SP")
        self.photonCalibLow  = PVAdjustable("SGE-OP2E-ARAMIS:PH2E_X1")
        self.photonCalibHigh = PVAdjustable("SGE-OP2E-ARAMIS:PH2E_X2")
        self.ebeamCalibLow   = PVAdjustable("SGE-OP2E-ARAMIS:PH2E_Y1")
        self.ebeamCalibHigh  = PVAdjustable("SGE-OP2E-ARAMIS:PH2E_Y2")
        self.dcmMoving       = PVAdjustable("SAROP11-ODCM105:MOVING")
        self.dcmStop         = PVAdjustable("SAROP11-ODCM105:STOP.PROC")

        self.energy = CoupledDoubleCrystalMonoEnergy(Id, name=name)



class CoupledDoubleCrystalMonoEnergy(Adjustable):

    def __init__(self, Id, name=None):
        pvname_setvalue = "SAROP11-ARAMIS:ENERGY_SP_USER"
        pvname_readback = "SAROP11-ARAMIS:ENERGY"
        pvname_moving   = "SGE-OP2E-ARAMIS:MOVING"
        pvname_coupling = "SGE-OP2E-ARAMIS:MODE_SP"

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback)
        pv_moving   = PV(pvname_moving)
        pv_coupling = PV(pvname_coupling)

        name = name or Id
        units = pv_readback.units
        super().__init__(name=name, units=units)

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback,
            moving   = pvname_moving,
            coupling = pvname_coupling
        )

        self.pvs = SimpleNamespace(
            setvalue = pv_setvalue,
            readback = pv_readback,
            moving   = pv_moving,
            coupling = pv_coupling
        )


    def get_current_value(self):
        return self.pvs.readback.get()

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold)

    def move_and_wait(self, value, wait_time=0.1):
        self.enable_coupling()
        self.pvs.setvalue.put(value)
        while self.is_moving():
            sleep(wait_time)

    def is_moving(self):
        done = self.pvs.moving.get()
        return not bool(done)

    def enable_coupling(self):
        self.pvs.coupling.put(1)

    def disable_coupling(self):
        self.pvs.coupling.put(0)

    @property
    def coupling(self):
        return self.pvs.coupling.get(as_string=True)



