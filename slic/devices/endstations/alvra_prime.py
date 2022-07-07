from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor
from slic.devices.general.smaract import SmarActAxis
from slic.utils.printing import printable_dict


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



class Vacuum(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)
        self.KBvalve           = PVEnumAdjustable(ID + "VPG124-230:PLC_OPEN")
        self.spectrometerP     = PVAdjustable(ID + "MFR125-600:PRESSURE")
        self.intermediateP     = PVAdjustable(ID + "MCP125-510:PRESSURE")
        self.sampleP           = PVAdjustable(ID + "MCP125-410:PRESSURE")
        self.spectrometerTurbo = PVAdjustable(ID + "PTM125-600:HZ")
        self.intermediateTurbo = PVAdjustable(ID + "PTM125-500:HZ")
        self.sampleTurbo       = PVAdjustable(ID + "PTM125-400:HZ")
        self.pDiff             = PVAdjustable("SARES11-EVSP-010:DIFFERENT")
        self.regulationStatus  = PVAdjustable("SARES11-EVGA-STM010:ACTIV_MODE")


    def __repr__(self):
        current = {}
        current["KB valve"] = "open" if self.KBvalve.get_current_value() == "ON" else "closed"

        current["Regulation mode"]                         = str(self.regulationStatus)
        current["Spectrometer pressure"]                   = str(self.spectrometerP)
        current["Spectrometer turbo pump"]                 = str(self.spectrometerTurbo)
        current["Intermediate pressure"]                   = str(self.intermediateP)
        current["Intermediate turbo pump"]                 = str(self.intermediateTurbo)
        current["Sample pressure"]                         = str(self.sampleP)
        current["Sample turbo pump"]                       = str(self.sampleTurbo)
        current["Intermediate/Sample pressure difference"] = str(self.pDiff)

        return printable_dict(current, "Prime chamber vacuum status")



