from slic.devices.general.motor import Motor
from slic.devices.general.detectors import CameraCA, CameraBS


class Bernina_XEYE:

    def __init__(self, camera_pv=None, zoomstage_pv=None, bshost=None, bsport=None):

        try:
            self.zoom = Motor(zoomstage_pv)
        except:
            print("X-Ray eye zoom motor not found")

        try:
            self.cam = CameraCA(camera_pv)
        except:
            print("X-Ray eye Cam not found")

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)


    def __repr__(self):
        ostr = "*****Xeye motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr



