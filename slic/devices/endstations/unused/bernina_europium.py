from epics import PV
from slic.devices.general.motor import Motor


class EXP:

    def __init__(self, Id, alias_namespace=None):
        self.Id = Id

        ### motors 1.5M JF Zaber ###
        #self.det_x = Motor(Id + ':MOT_TX')
        #self.det_y = Motor(Id + ':MOT_TY')
        self.zaber_x = Motor(Id + ":MOT_TZ")
        self.qioptiq_zoom = Motor(Id + ":MOT_QIOPT_Z")

        ### motors crystal ###
        #self.c_focus = Motor(Id + ':MOT_VT80')
        #self.c_rot = Motor(Id + ':MOT_ROT')

    def __repr__(self):
        s = "**Detector and crystal positions**\n"
        motors = "zaber_x qioptiq_zoom".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"

        return s



