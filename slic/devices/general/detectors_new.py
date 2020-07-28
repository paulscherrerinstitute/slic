import numpy as np
from epics import caget
from epics import PV
from slic.utils.eco_epics.utilities_epics import EnumWrapper

# from cam_server import PipelineClient
# from cam_server.utils import get_host_port_from_stream_address
# from bsread import source, SUB
import subprocess
import h5py
from time import sleep, time
from datetime import datetime

from slic.core.task import Task
from slic.utils.eco_components.aliases import Alias


class PvDataStream:

    def __init__(self, Id, name=None):
        self.Id = Id
        self._pv = PV(Id)
        self.name = name
        self.alias = Alias(self.name, channel=self.Id, channeltype="CA")

    def collect(self, seconds=None, samples=None):
        if (not seconds) and (not samples):
            raise Exception("Either a time interval or number of samples need to be defined.")
        try:
            self._pv.callbacks.pop(self._collection["ix_cb"])
        except:
            pass
        self._collection = {"done": False}
        self.data_collected = []
        if seconds:
            self._collection["start_time"] = time()
            self._collection["seconds"] = seconds
            stopcond = lambda: (time() - self._collection["start_time"]) > self._collection["seconds"]

            def addData(**kw):
                if not stopcond():
                    self.data_collected.append(kw["value"])
                else:
                    self._pv.callbacks.pop(self._collection["ix_cb"])
                    self._collection["done"] = True

        elif samples:
            self._collection["samples"] = samples
            stopcond = lambda: len(self.data_collected) >= self._collection["samples"]

            def addData(**kw):
                self.data_collected.append(kw["value"])
                if stopcond():
                    self._pv.callbacks.pop(self._collection["ix_cb"])
                    self._collection["done"] = True

        self._collection["ix_cb"] = self._pv.add_callback(addData)
        while not self._collection["done"]:
            sleep(0.005)
        return self.data_collected

    def acquire(self, hold=False, **kwargs):
        _acquire = lambda: self.collect(**kwargs)
        return Task(_acquire, hold=hold)

    def accumulate(self, n_buffer):
        if not hasattr(self, "_accumulate"):
            self._accumulate = {"n_buffer": n_buffer, "ix": 0, "n_cb": -1}
        else:
            self._accumulate["n_buffer"] = n_buffer
            self._accumulate["ix"] = 0
        self._pv.callbacks.pop(self._accumulate["n_cb"], None)
        self._data = np.squeeze(np.zeros([n_buffer * 2, self._pv.count])) * np.nan

        def addData(**kw):
            self._accumulate["ix"] = (self._accumulate["ix"] + 1) % self._accumulate["n_buffer"]
            self._data[self._accumulate["ix"] :: self._accumulate["n_buffer"]] = kw["value"]

        self._accumulate["n_cb"] = self._pv.add_callback(addData)

    def get_data(self):
        return self._data[self._accumulate["ix"] + 1 : self._accumulate["ix"] + 1 + self._accumulate["n_buffer"]]

    data = property(get_data)


_cameraArrayTypes = ["monochrome", "rgb"]


class CameraCA:

    def __init__(self, pvname, cameraArrayType="monochrome", elog=None):
        self.Id = pvname
        self.isBS = False
        self.px_height = None
        self.px_width = None
        self.elog = elog

    def get_px_height(self):
        if not self.px_height:
            self.px_height = caget(self.Id + ":HEIGHT")
        return self.px_height

    def get_px_width(self):
        if not self.px_width:
            self.px_width = caget(self.Id + ":WIDTH")
        return self.px_width

    def get_data(self):
        w = int(self.get_px_width())
        h = int(self.get_px_height())
        numpix = int(caget(self.Id + ":FPICTURE.NORD"))
        i = caget(self.Id + ":FPICTURE", count=numpix)
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

        cmd.append('"NAME=%s,CAMNAME=%s"' % (self.Id, self.Id))
        cmd.append("/sf/controls/config/qt/Camera/CameraMiniView.ui")
        return subprocess.Popen(" ".join(cmd), shell=True)


# /sf/controls/config/qt/Camera/CameraMiniView.ui" with macro "NAME=SAROP21-PPRM138,CAMNAME=SAROP21-PPRM138


class CameraBS:

    def __init__(self, host=None, port=None, elog=None):
        self._stream_host = host
        self._stream_port = port

    def checkServer(self):
        # Check if your instance is running on the server.
        if self._instance_id not in client.get_server_info()["active_instances"]:
            raise ValueError("Requested pipeline is not running.")

    def get_images(self, N_images):
        data = []
        with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:
            input_stream.connect()

            for n in range(N_images):
                data.append(input_stream.receive().data.data["image"].value)
        return data

    def record_images(self, fina, N_images, dsetname="images"):
        ds = None
        with h5py.File(fina, "w") as f:
            with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:

                input_stream.connect()

                for n in range(N_images):
                    image = input_stream.receive().data.data["image"].value
                    if not ds:
                        ds = f.create_dataset(dsetname, dtype=image.dtype, shape=(N_images,) + image.shape)
                    ds[n, :, :] = image


class FeDigitizer:

    def __init__(self, Id, elog=None):
        self.Id = Id
        self.gain = EnumWrapper(Id + "-WD-gain")
        self._bias = PV(Id + "-HV_SET")
        self.channels = [
            Id + "-BG-DATA",
            Id + "-BG-DRS_TC",
            Id + "-BG-PULSEID-valid",
            Id + "-DATA",
            Id + "-DRS_TC",
            Id + "-PULSEID-valid",
        ]

    def set_bias(self, value):
        self._bias.put(value)

    def get_bias(self):
        return self._bias.value


class DiodeDigitizer:

    def __init__(self, Id, VME_crate=None, link=None, ch_0=7, ch_1=8, elog=None):
        self.Id = Id
        if VME_crate:
            self.diode_0 = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_0))
            self.diode_1 = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_1))



