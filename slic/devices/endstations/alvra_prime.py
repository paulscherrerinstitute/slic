from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor
from slic.devices.general.smaract import SmarActAxis
from slic.utils.hastyepics import get_pv as PV


class PrimeTable(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.mode   = PVEnumAdjustable(ID + ":MODE_SP")
        self.status = PVAdjustable(ID + ":SS_STATUS")

        self.motors = SimpleDevice("Motors",
            x1 = Motor(ID + ":MOTOR_X1"),
            y1 = Motor(ID + ":MOTOR_Y1"),
            y2 = Motor(ID + ":MOTOR_Y2"),
            y3 = Motor(ID + ":MOTOR_Y3"),
            z1 = Motor(ID + ":MOTOR_Z1"),
            z2 = Motor(ID + ":MOTOR_Z2")
        )

        self.w = SimpleDevice("W",
            x      = Motor(ID + ":W_X"),
            y      = Motor(ID + ":W_Y"),
            z      = Motor(ID + ":W_Z"),
            pitch  = Motor(ID + ":W_RX"),
            yaw    = Motor(ID + ":W_RY"),
            roll   = Motor(ID + ":W_RZ")
        )



class VonHamosBragg(Device):

    def __init__(self, ID, name="von Hamos positions", **kwargs):
        super().__init__(ID, name=name, **kwargs)
        self.cry1 = Motor(ID + ":CRY_1", name = name + " Crystal 1")
        self.cry2 = Motor(ID + ":CRY_2", name = name + " Crystal 2")



class Microscope(Device):

    def __init__(self, ID, gonio=None, rotat=None, name="Microscope positions", **kwargs):
        super().__init__(ID, name=name, **kwargs)
        self.focus = Motor(ID + ":FOCUS")
        self.zoom  = Motor(ID + ":ZOOM")
        self.gonio = SmarActAxis(gonio) if gonio else None
        self.rotat = SmarActAxis(rotat) if rotat else None



class Vacuum:

    def __init__(self, ID, z_undulator=None, description=None):
        self.ID = ID

        # Vacuum PVs for Prime chamber
        self.spectrometerP = PV(ID + "MFR125-600:PRESSURE")
        self.intermediateP = PV(ID + "MCP125-510:PRESSURE")
        self.sampleP = PV(ID + "MCP125-410:PRESSURE")
        self.pDiff = PV("SARES11-EVSP-010:DIFFERENT")
        self.regulationStatus = PV("SARES11-EVGA-STM010:ACTIV_MODE")
        self.spectrometerTurbo = PV(ID + "PTM125-600:HZ")
        self.intermediateTurbo = PV(ID + "PTM125-500:HZ")
        self.sampleTurbo = PV(ID + "PTM125-400:HZ")
        self.KBvalve = PV(ID + "VPG124-230:PLC_OPEN")

    def __str__(self):
        valve = self.KBvalve.get()
        if valve == 0:
            valveStr = "KB valve closed"
        else:
            valveStr = "KB valve open"
        currSpecP = self.spectrometerP.get()
        currInterP = self.intermediateP.get()
        currSamP = self.sampleP.get()
        currPDiff = self.pDiff.get()
        regStatusStr = self.regulationStatus.get(as_string=True)
        currSpecTurbo = self.spectrometerTurbo.get()
        currInterTurbo = self.intermediateTurbo.get()
        currSamTurbo = self.sampleTurbo.get()

        s = "**Prime chamber vacuum status**\n\n"
        s += "Regulation mode: %s\n" % regStatusStr
        s += "%s\n" % valveStr
        s += "Spectrometer pressure: %.3g mbar\n" % currSpecP
        s += "Spectrometer Turbo pump: %s Hz\n" % currSpecTurbo
        s += "Intermediate pressure: %.3g mbar\n" % currInterP
        s += "Intermediate Turbo pump: %s Hz\n" % currInterTurbo
        s += "Sample pressure: %.3g mbar\n" % currSamP
        s += "Sample Turbo pump: %s Hz\n" % currSamTurbo
        s += "Intermediate/Sample pressure difference: %.3g mbar\n" % currPDiff
        return s

    def __repr__(self):
        return self.__str__()



