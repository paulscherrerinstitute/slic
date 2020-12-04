from types import SimpleNamespace
from time import sleep
import numpy as np
from epics import PV

from slic.core.adjustable import Adjustable
from slic.devices.general.motor import Motor
from ..device import Device


class EcolEnergy:

    def __init__(self, Id, val="SARCL02-MBND100:P-SET", rb="SARCL02-MBND100:P-READ", dmov="SFB_BEAM_ENERGY_ECOL:SUM-ERROR-OK"):
        self.Id = Id
        self.setter = PV(val)
        self.readback = PV(rb)
        self.dmov = PV(dmov)
        self.done = False

    def get_current_value(self):
        return self.readback.get()

    def move_and_wait(self, value, checktime=0.01, precision=2):
        curr = self.setter.get()
        while abs(curr - value) > 0.1:
            curr = self.setter.get()
            self.setter.put(curr + np.sign(value - curr) * 0.1)
            sleep(0.3)

        self.setter.put(value)
        while abs(self.get_current_value() - value) > precision:
            sleep(checktime)
        while not self.dmov.get():
            # print(self.dmov.get())
            sleep(checktime)

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold)





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

    def move_and_wait(self, value, checktime=0.01, precision=0.5):
        self.set_current_value(value)
        while abs(self.wait_for_valid_value() - value) > precision:
            sleep(checktime)

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


class AlvraDCM_FEL:

    def __init__(self, Id):
        self.Id = Id
        self.name = "Alvra DCM monochromator coupled to FEL beam"
#        self.IOCstatus = PV('ALVRA:running')                    # bool 0 running, 1 not running
        self._FELcoupling = PV("SGE-OP2E-ARAMIS:MODE_SP")       # string "Off" or "e-beam"
        self._setEnergy = PV("SAROP11-ARAMIS:ENERGY_SP_USER")   # float eV
        self._getEnergy = PV("SAROP11-ARAMIS:ENERGY")           # float eV
        self.ebeamEnergy = PV("SARCL02-MBND100:P-READ")         # float MeV/c
        self.ebeamEnergySP = PV("SGE-OP2E-ARAMIS:E_ENERGY_SP")  # float MeV
        self.dcmStop = PV("SAROP11-ODCM105:STOP.PROC")          # stop the DCM motors
        self.dcmMoving = PV("SAROP11-ODCM105:MOVING")           # DCM moving field
        self._energyChanging = PV("SGE-OP2E-ARAMIS:MOVING")     # PV telling you something related to the energy is changing
        self._alvraMode = PV("SAROP11-ARAMIS:MODE")             # string Aramis SAROP11 mode
        self.ebeamOK = PV("SFB_BEAM_ENERGY_ECOL:SUM-ERROR-OK")  # is ebeam no longer changing
        self.photCalib1 = PV("SGE-OP2E-ARAMIS:PH2E_X1")         # photon energy calibration low calibration point
        self.photCalib2 = PV("SGE-OP2E-ARAMIS:PH2E_X2")         # photon energy calibration high calibration point
        self.ebeamCalib1 = PV("SGE-OP2E-ARAMIS:PH2E_Y1")        # electron energy calibration low calibration point
        self.ebeamCalib2 = PV("SGE-OP2E-ARAMIS:PH2E_Y2")        # electron energy calibration high calibration point

    def __str__(self):
#        ioc = self.IOCstatus.get()
#        if ioc == 0:
#            iocStr = "Soft IOC running"
#        else:
#            iocStr = "Soft IOC not running"
        FELcouplingStr = self._FELcoupling.get(as_string=True)
        alvraModeStr = self._alvraMode.get(as_string=True)
        currEnergy = self._getEnergy.get()
        currebeamEnergy = self.ebeamEnergy.get()
        photCalib1Str = self.photCalib1.get()
        photCalib2Str = self.photCalib2.get()
        ebeamCalib1Str = self.ebeamCalib1.get()
        ebeamCalib2Str = self.ebeamCalib2.get()

        s = "**Alvra DCM-FEL status**\n\n"
#        print('%s'%iocStr)
#        print('FEL coupling %s'%FELcouplingStr)
#        print('Alvra beamline mode %s'%alvraModeStr)
#        print('Photon energy (eV) %'%currEnergy)
#        s += '%s\n'%iocStr
        s += "FEL coupling: %s\n" % FELcouplingStr
        s += "Alvra beamline mode: %s\n" % alvraModeStr
        s += "Photon energy: %.2f eV\n" % currEnergy
        s += "Electron energy: %.2f MeV\n" % currebeamEnergy
        s += "Calibration set points:\n"
        s += "   Low: Photon %.2f keV, Electron %.2f MeV\n" % (photCalib1Str, ebeamCalib1Str)
        s += "   High: Photon %.2f keV, Electron %.2f MeV\n" % (photCalib2Str, ebeamCalib2Str)
        return s

    def get_current_value(self):
        return self._getEnergy.get()

    def move_and_wait(self, value, checktime=0.1, precision=0.5):
        self._FELcoupling.put(1)  # ensure the FEL coupling is turned on
        self._setEnergy.put(value)
#        while self.ebeamOK.get()==0:
#            sleep(checktime)
#        while abs(self.ebeamEnergy.get()-self.ebeamEnergySP.get())>precision:
#            sleep(checktime)
#        while self.dcmMoving.get()==1:
#            sleep(checktime)
        while self._energyChanging == 1:
            sleep(checktime)

    def set_target_value(self, value, hold=False):
        changer = lambda: self.move_and_wait(value)
        return Task(changer, hold=hold)

    def __repr__(self):
        return self.__str__()



