from slic.core.adjustable import PVAdjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor
from slic.devices.general.detectors import CameraCA, CameraBS


class CameraSigma(Device):

    def __init__(self, zoomstage_pvs=None, camera_pv=None, bshost=None, bsport=None, name="Sigma objective", **kwargs):
        super().__init__("SIGMA", name=name, **kwargs)

        if zoomstage_pvs:
            self.zoom = PVAdjustable(zoomstage_pvs["set_value"], zoomstage_pvs["readback"])

        if camera_pv:
            self.cam = CameraCA(camera_pv)

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)


class CameraQioptiq:

    def __init__(self, zoomstage_pv=None, focusstage_pv=None, camera_pv=None, bshost=None, bsport=None, name="Qioptic sample viewer", **kwargs):
        super().__init__("QIOPTIQ", name=name, **kwargs)

        if zoomstage_pv:
            self.zoom = Motor(zoomstage_pv)

        if focusstage_pv:
            self.focus = Motor(focusstage_pv)

        if camera_pv:
            self.cam = CameraCA(camera_pv)

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)



