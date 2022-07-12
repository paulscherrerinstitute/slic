from slic.devices.general.motor import Motor
from slic.devices.general.detectors import CameraCA, CameraBS
from slic.core.adjustable import PVEnumAdjustable


class Pprm:

    def __init__(self, ID, name=None):
        self.ID = ID
        self.name = name
        self.target_pos = Motor(ID + ":MOTOR_PROBE", name="target_pos")
        self.cam = CameraCA(ID)
        self.led = PVEnumAdjustable(ID + ":LED", name="led")
        self.target = PVEnumAdjustable(ID + ":PROBE_SP", name="target")

    def movein(self, target=1):
        self.target.set_target_value(target)

    def moveout(self, target=0):
        self.target.set_target_value(target)

    def illuminate(self, value=None):
        if value:
            self._led.put(value)
        else:
            self._led.put(not self.get_illumination_state())

    def get_illumination_state(self):
        return bool(self._led.get())

    def __repr__(self):
        s = f"**Profile Monitor {self.name}**\n"
        s += f"Target in beam: {self.target.get_current_value().name}\n"
        return s


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



#        self._led = PV(self.ID + ':LED')


#    def illuminate(self,value=None):
#        if value:
#            self._led.put(value)
#        else:
#            self._led.put(
#                    not self.get_illumination_state())
#
#    def get_illumination_state(self):
#        return bool(self._led.get())
#



