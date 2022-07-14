_cameraArrayTypes = ["monochrome", "rgb"]


class CameraCA:

    def __init__(self, pvname, cameraArrayType="monochrome", elog=None):
        self.ID = pvname
        self.isBS = False
        self.px_height = None
        self.px_width = None
        self.elog = elog

    def get_px_height(self):
        if not self.px_height:
            self.px_height = caget(self.ID + ":HEIGHT")
        return self.px_height

    def get_px_width(self):
        if not self.px_width:
            self.px_width = caget(self.ID + ":WIDTH")
        return self.px_width

    def get_data(self):
        w = int(self.get_px_width())
        h = int(self.get_px_height())
        numpix = int(caget(self.ID + ":FPICTURE.NORD"))
        i = caget(self.ID + ":FPICTURE", count=numpix)
        return i.reshape(h, w)

    def record_images(self, fina, N_images, sleeptime=0.2):
        with h5py.File(fina, "w") as f:
            d = []
            for n in range(N_images):
                d.append(self.get_data())
                sleep(sleeptime)
            f["images"] = np.asarray(d)

    def gui(self, guiType="xdm"):
        """ Adjustable convention"""
        cmd = ["caqtdm", "-macro"]

        cmd.append('"NAME=%s,CAMNAME=%s"' % (self.ID, self.ID))
        cmd.append("/sf/controls/config/qt/Camera/CameraMiniView.ui")
        return subprocess.Popen(" ".join(cmd), shell=True)


# /sf/controls/config/qt/Camera/CameraMiniView.ui" with macro "NAME=SAROP21-PPRM138,CAMNAME=SAROP21-PPRM138



