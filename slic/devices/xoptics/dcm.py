from types import SimpleNamespace
from time import sleep
import numpy as np

from slic.core.adjustable import Adjustable, PVAdjustable, PVEnumAdjustable
from slic.utils.hastyepics import get_pv as PV
from slic.devices.general.motor import Motor
from ..device import Device


class DoubleCrystalMono(Device):

    def __init__(self, ID, name="Alvra DCM", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        self.theta  = Motor(ID + ":RX12")
        self.x      = Motor(ID + ":TX12")
        self.gap    = Motor(ID + ":T2")
        self.roll1  = Motor(ID + ":RZ1")
        self.roll2  = Motor(ID + ":RZ2")
        self.pitch2 = Motor(ID + ":RX2")

        self.energy = DoubleCrystalMonoEnergy(ID, name=name)



class DoubleCrystalMonoEnergy(Adjustable):

    def __init__(self, ID, name=None):
        self.wait_time = 0.1

        pvname_setvalue = "SAROP11-ARAMIS:ENERGY_SP"
        pvname_readback = "SAROP11-ARAMIS:ENERGY"
        pvname_moving   = "SAROP11-ODCM105:MOVING"
        pvname_stop     = "SAROP11-ODCM105:STOP.PROC"

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback)
        pv_moving   = PV(pvname_moving)
        pv_stop     = PV(pvname_stop)

        units = pv_readback.units
        super().__init__(ID, name=name, units=units)

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
        sleep(3)

    def set_target_value(self, value):
        self.set_current_value(value)
#        while abs(self.wait_for_valid_value() - value) > accuracy:
        while self.is_moving():
            sleep(self.wait_time)


    def wait_for_valid_value(self):
        val = np.nan
        while not np.isfinite(val):
            val = self.get_current_value()
        return val

    def is_moving(self):
        moving = self.pvs.moving.get()
        return bool(moving)

    def stop(self):
        self.pvs.stop.put(1)





class EcolEnergy:

    def __init__(self, ID, val="SARCL02-MBND100:P-SET", rb="SARCL02-MBND100:P-READ", dmov="SFB_BEAM_ENERGY_ECOL:SUM-ERROR-OK"):
        self.ID = ID
        self.setter = PV(val)
        self.readback = PV(rb)
        self.dmov = PV(dmov)
        self.done = False
        self.wait_time = 0.01
        self.accuracy = 2

    def get_current_value(self):
        return self.readback.get()

    def set_target_value(self, value):
        wait_time = self.wait_time
        accuracy = self.accuracy

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



class MonoEcolEnergy:

    def __init__(self, ID):
        self.ID = ID
        self.name = "energy_collimator"
        self.dcm = DoubleCrystalMono(ID)
        self.ecol = EcolEnergy("ecol_dummy")
        self.offset = None
        self.MeVperEV = 0.78333

    def get_current_value(self):
        return self.dcm.get_current_value()

    def set_target_value(self, value):
        ch = [self.dcm.set_target_value(value), self.ecol.set_target_value(self.calcEcol(value))]
        for tc in ch:
            tc.wait()

    def stop(self):
        self.dcm.stop()

    def alignOffsets(self):
        mrb = self.dcm.get_current_value()
        erb = self.ecol.get_current_value()
        self.offset = {"dcm": mrb, "ecol": erb}

    def calcEcol(self, eV):
        return (eV - self.offset["dcm"]) * self.MeVperEV + self.offset["ecol"]





class CoupledDoubleCrystalMono(Device):

    def __init__(self, ID, name="Alvra DCM coupled to FEL energy", **kwargs):
        super().__init__(ID, name=name, **kwargs)

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

        self.energy = CoupledDoubleCrystalMonoEnergy(ID, name=name)



class CoupledDoubleCrystalMonoEnergy(Adjustable):

    def __init__(self, ID, name=None):
        self.wait_time = 0.1

        pvname_setvalue = "SAROP11-ARAMIS:ENERGY_SP"
        pvname_readback = "SAROP11-ARAMIS:ENERGY"
#        pvname_moving   = "SGE-OP2E-ARAMIS:MOVING" #TODO: this seems broken?
        pvname_moving   = "SAROP11-ODCM105:MOVING"
        pvname_coupling = "SGE-OP2E-ARAMIS:MODE_SP"

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback)
        pv_moving   = PV(pvname_moving)
        pv_coupling = PV(pvname_coupling)

        units = pv_readback.units
        super().__init__(ID, name=name, units=units)

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

    def set_target_value(self, value):
        self.enable_coupling()
        self.pvs.setvalue.put(value)
        sleep(3)
        while self.is_moving():
            sleep(self.wait_time)

    def is_moving(self):
        moving = self.pvs.moving.get()
        return bool(moving)

    def enable_coupling(self):
        self.pvs.coupling.put(1)

    def disable_coupling(self):
        self.pvs.coupling.put(0)

    @property
    def coupling(self):
        return self.pvs.coupling.get(as_string=True)



class CoupledDoubleCrystalMonoEnergyWithTimeCorrection(Adjustable):

    def __init__(self, ID="CDCMEWTC", name="Alvra DCM coupled to FEL energy with time correction", limit_low=None, limit_high=None):
        self.wait_time = 0.1

        self.limit_low = limit_low
        self.limit_high = limit_high

        pvname_setvalue = "SAROP11-ARAMIS:ENERGY_SP" #_USER" #TODO: where did the _USER go?
        pvname_readback = "SAROP11-ARAMIS:ENERGY"
#        pvname_moving   = "SGE-OP2E-ARAMIS:MOVING"
        pvname_moving   = "SAROP11-ODCM105:MOVING"
        pvname_coupling = "SGE-OP2E-ARAMIS:MODE_SP"

        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback)
        pv_moving   = PV(pvname_moving)
        pv_coupling = PV(pvname_coupling)

        self.timing = Motor("SLAAR11-LMOT-M452:MOTOR_1")
        self.electron_energy_rb = PV("SARCL02-MBND100:P-READ")
        self.electron_energy_sv = PV("SGE-OP2E-ARAMIS:E_ENERGY_SP")

        units = pv_readback.units
        super().__init__(ID, name=name, units=units)

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
        ll = self.limit_low
        if ll is not None:
            if value < ll:
                msg = f"requested value is outside the allowed range: {value} < {ll}"
                print(msg)
                raise KeyboardInterrupt(msg)
        lh = self.limit_high
        if lh is not None:
            if value > lh:
                msg = f"requested value is outside the allowed range: {value} > {lh}"
                print(msg)
                raise KeyboardInterrupt(msg)

        wait_time = self.wait_time

        self.enable_coupling()

        current_energy = self.get_current_value()
        delta_energy = value - current_energy

        timing = self.timing
        current_delay = timing.get_current_value()
        delta_delay = convert_E_to_distance(delta_energy)
        target_delay = current_delay + delta_delay

        print(f"Energy = {current_energy} -> delta = {delta_energy} -> {value}")
        print(f"Delay  = {current_delay}  -> delta = {delta_delay}  -> {target_delay}")

        timing.set_target_value(target_delay).wait()

        self.pvs.setvalue.put(value)
        sleep(3) # wait so that the set value has changed

        print("start waiting for DCM")
        while self.is_moving(): #TODO: moving PV seems broken
            sleep(wait_time)
        print("start waiting for electron beam")
        while abs(self.electron_energy_rb.get() - self.electron_energy_sv.get()) > 0.25:
            sleep(wait_time)
        sleep(wait_time)


    def is_moving(self):
        moving = self.pvs.moving.get()
        return bool(moving)

    def enable_coupling(self):
        self.pvs.coupling.put(1)

    def disable_coupling(self):
        self.pvs.coupling.put(0)

    @property
    def coupling(self):
        return self.pvs.coupling.get(as_string=True)



def convert_E_to_distance(E):
    return 0.0061869 * E



