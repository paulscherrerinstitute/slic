from slic.core.adjustable import PVAdjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor
from slic.devices.cameras import CameraCA, CameraBS


class CameraSigma(Device):

    def __init__(self, ID="SIGMA", zoomstage_pvs=None, camera_pv=None, bshost=None, bsport=None, name="Sigma objective", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        if zoomstage_pvs:
            self.zoom = PVAdjustable(zoomstage_pvs["set_value"], zoomstage_pvs["readback"])

        if camera_pv:
            self.cam = CameraCA(camera_pv)

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)


class CameraQioptiq(Device):

    def __init__(self, ID="QIOPTIQ", zoomstage_pv=None, focusstage_pv=None, camera_pv=None, bshost=None, bsport=None, name="Qioptic sample viewer", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        if zoomstage_pv:
            self.zoom = Motor(zoomstage_pv)

        if focusstage_pv:
            self.focus = Motor(focusstage_pv)

        if camera_pv:
            self.cam = CameraCA(camera_pv)

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)


class XEye(Device):

    def __init__(self, ID="XEYE", zoomstage_pv=None, camera_pv=None, bshost=None, bsport=None, name="XEye", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        if zoomstage_pv:
            self.zoom = Motor(zoomstage_pv)

        if camera_pv:
            self.cam = CameraCA(camera_pv)

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)



