from slic.utils.hastyepics import get_pv as PV

from .camerabase import CameraBase


class CameraCA(CameraBase):

    def __init__(self, ID, wait_time=0.2):
        self.ID = ID
        self.wait_time = wait_time

        self.pv_image  = PV(ID + ":FPICTURE")
        self.pv_size   = PV(ID + ":FPICTURE.NORD")
        self.pv_height = PV(ID + ":HEIGHT")
        self.pv_width  = PV(ID + ":WIDTH")


    @property
    def size(self):
        return int(self.pv_size.get())

    @property
    def shape(self):
        return (self.height, self.width)

    @property
    def height(self):
        return int(self.pv_height.get())

    @property
    def width(self):
        return int(self.pv_width.get())


    def get_image(self):
        img = self.pv_image.get(count=self.size)
        return img.reshape(self.shape)

    def _iterate_receive(self, n):
        for i in range(n):
            img = self.get_image()
            yield img
            sleep(self.wait_time)


    def gui(self):
        ID = self.ID
        cmd = [
            "caqtdm",
            "-macro",
            f'"NAME={ID},CAMNAME={ID}"',
            "/sf/controls/config/qt/Camera/CameraMiniView.ui"
        ]
        return subprocess.Popen(cmd, shell=True)



