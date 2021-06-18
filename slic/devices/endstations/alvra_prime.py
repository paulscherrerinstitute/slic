from epics import PV
from slic.devices.general.motor import Motor
from ..general.smaract import SmarActAxis


class Huber:

    def __init__(self, Id, alias_namespace=None, z_undulator=None, description=None, name="Prime Sample Manipulator"):
        self.Id = Id

        ### Huber sample stages ###
        self.x = Motor(Id + ":MOTOR_X1", name + " X")
        self.y = Motor(Id + ":MOTOR_Y1", name + " Y")
        self.z = Motor(Id + ":MOTOR_Z1", name + " Z")

    def __str__(self):
        return "Huber Sample Stage %s\nx: %s mm\ny: %s mm\nz: %s mm" % (self.Id, self.x.wm(), self.y.wm(), self.z.wm())

    def __repr__(self):
        return "{'X': %s, 'Y': %s, 'Z': %s}" % (self.x.wm(), self.y.wm(), self.z.wm())


class VonHamosBragg:

    def __init__(self, Id, alias_namespace=None, z_undulator=None, description=None):
        self.Id = Id

        ### Owis linear stages ###
        self.cry1 = Motor(Id + ":CRY_1")
        self.cry2 = Motor(Id + ":CRY_2")

    def __str__(self):
        return "von Hamos positions\nCrystal 1: %s mm\nCrystal 2: %s mm" % (self.cry1.wm(), self.cry2.wm())

    def __repr__(self):
        return "{'Crystal 1': %s, 'Crystal 2': %s}" % (self.cry1.wm(), self.cry2.wm())


class Table:

    def __init__(self, Id, alias_namespace=None, z_undulator=None, description=None):
        self.Id = Id

        ### ADC optical table ###
        self.x1 = Motor(Id + ":MOTOR_X1")
        self.y1 = Motor(Id + ":MOTOR_Y1")
        self.y2 = Motor(Id + ":MOTOR_Y2")
        self.y3 = Motor(Id + ":MOTOR_Y3")
        self.z1 = Motor(Id + ":MOTOR_Z1")
        self.z2 = Motor(Id + ":MOTOR_Z2")
        self.x = Motor(Id + ":W_X")
        self.y = Motor(Id + ":W_Y")
        self.z = Motor(Id + ":W_Z")
        self.pitch = Motor(Id + ":W_RX")
        self.yaw = Motor(Id + ":W_RY")
        self.roll = Motor(Id + ":W_RZ")
        self.modeSP = PV(Id + ":MODE_SP")
        self.status = PV(Id + ":SS_STATUS")

    def __str__(self):
        return "Prime Table position\nx: %s mm\ny: %s mm\nz: %s\npitch: %s mrad\nyaw: %s mrad\nmode SP: %s \nstatus: %s" % (self.x.wm(), self.y.wm(), self.z.wm(), self.pitch.wm(), self.yaw.wm(), self.modeSP.get(as_string=True), self.status.get())

    def __repr__(self):
        return "{'x': %s, 'y': %s,'z': %s,'pitch': %s, 'yaw': %s, 'mode set point': %s,'status': %s}" % (self.x, self.y, self.z, self.pitch, self.yaw, self.modeSP.get(as_string=True), self.status.get())


class Microscope:

    def __init__(self, Id, gonio=None, rotat=None, alias_namespace=None, z_undulator=None, description=None):
        self.Id = Id

        ### Microscope motors ###
        self.focus = Motor(Id + ":FOCUS")
        self.zoom = Motor(Id + ":ZOOM")
#        self._smaractaxes = {
#            'gonio': '_xmic_gon',   # will become self.gonio
#            'rot':   '_xmic_rot'}   # """ self.rot
        self.gonio = SmarActAxis(gonio) #TODO: can this be None?
        self.rot = SmarActAxis(rotat) #TODO: can this be None?

    def __str__(self):
        return "Microscope positions\nfocus: %s\nzoom:  %s\ngonio: %s\nrot:   %s" % (self.focus.wm(), self.zoom.wm(), self.gonio.wm(), self.rot.wm())

    def __repr__(self):
        return "{'Focus': %s, 'Zoom': %s, 'Gonio': %s, 'Rot': %s}" % (self.focus.wm(), self.zoom.wm(), self.gonio.wm(), self.rot.wm())


# prism (as a SmarAct-only stage) is defined purely in ../aliases/alvra.py


class Vacuum:

    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id

        # Vacuum PVs for Prime chamber
        self.spectrometerP = PV(Id + "MFR125-600:PRESSURE")
        self.intermediateP = PV(Id + "MCP125-510:PRESSURE")
        self.sampleP = PV(Id + "MCP125-410:PRESSURE")
        self.pDiff = PV("SARES11-EVSP-010:DIFFERENT")
        self.regulationStatus = PV("SARES11-EVGA-STM010:ACTIV_MODE")
        self.spectrometerTurbo = PV(Id + "PTM125-600:HZ")
        self.intermediateTurbo = PV(Id + "PTM125-500:HZ")
        self.sampleTurbo = PV(Id + "PTM125-400:HZ")
        self.KBvalve = PV(Id + "VPG124-230:PLC_OPEN")

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



