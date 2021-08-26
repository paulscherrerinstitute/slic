from epics import PV
from slic.devices.general.motor import Motor


class EXP:

    def __init__(self, ID, alias_namespace=None):
        self.ID = ID

        ### motors 1.5M JF Zaber ###
#        self.det_x = Motor(ID + ':MOT_TX')
#        self.det_y = Motor(ID + ':MOT_TY')
        self.zaber_x = Motor(ID + ":MOT_TZ")
        self.qioptiq_zoom = Motor(ID + ":MOT_QIOPT_Z")

        ### motors crystal ###
#        self.c_focus = Motor(ID + ':MOT_VT80')
#        self.c_rot = Motor(ID + ':MOT_ROT')

    def __repr__(self):
        s = "**Detector and crystal positions**\n"
        motors = "zaber_x qioptiq_zoom".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"

        return s



