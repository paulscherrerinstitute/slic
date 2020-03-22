import os
from datetime import datetime
from time import sleep
from detector_integration_api import DetectorIntegrationClient

from ..utils.channels import Channels
from ..utils.printing import printable_dict_of_dicts
from .acquisition import Acquisition
from .basecounter import BaseCounter
from .utils import can_create_file, SwissFELPaths
from .pedestals import find_last_pedestal



EXPTIME = {
    "alvra":   0.000005,
    "bernina": 0.00001
}



class DIACounter(BaseCounter):

    def __init__(self, instrument, pgroup, default_channels=None, default_path=None, api_address=None):
        self.instrument = instrument
        self.pgroup = pgroup

        self.config = DIAConfig(instrument, pgroup)
        self.paths = SwissFELPaths(instrument, pgroup)

        if not default_channels:
            default_channel_list = self.paths.default_channel_list
            default_channels = Channels(default_channel_list)

        if not default_path:
            default_path = self.paths.raw

        self.default_channels = default_channels
        self.default_path = default_path

        if not api_address:
            api_address = "http://sf-daq-{}:10000".format(instrument)

        self.api_address = api_address
        self.client = DetectorIntegrationClient(api_address)


    def acquire(self, filename=None, channels=None, n_pulses=100, use_default_path=True, is_HG0=False, **kwargs):
        if filename:
            if use_default_path:
                filename = os.path.join(self.default_path, filename)
            if not self.can_create_all_files(filename):
                return
        else:
            filename = "/dev/null"

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        if not is_HG0:
            self.clear_HG0_bit()

        gain_file = self.paths.gain
        pede_file = self.get_last_pedestal()

        cfg = self.config.to_dict(filename=filename, channels=channels, n_pulses=n_pulses, gain_file=gain_file, pede_file=pede_file, is_HG0=is_HG0)
        self.set_config(cfg)

        def _acquire():
            self.client.start()
            self.wait_until_finished()
            self.client.reset()

        return Acquisition(acquire=_acquire, stopper=self.client.stop, hold=False)


    def can_create_all_files(self, base):
        for client in self.active_clients:
            client = client.upper()
            filename = "{}.{}.h5".format(base, client)
            if not can_create_file(filename):
                return False
        return True

    @property
    def active_clients(self):
        cs = self.client.get_clients_enabled()
        cs = cs["clients_enabled"]
        cs = cs.keys()
        return sorted(cs)

    def clear_HG0_bit(self):
        self.client.set_detector_value("clearbit", "0x5d 0")

    def set_config(self, cfg):
        self.client.reset()
        self.client.set_config(cfg)
        self.client.wait_for_status("IntegrationStatus.CONFIGURED")

    def wait_until_finished(self, wait_time=0.5):
        while True:
            if self.status == "FINISHED": #TODO: in ("INITIALIZED", "DETECTOR_STOPPED", "BSREAD_STILL_RUNNING", "FINISHED") ?
                break
            sleep(wait_time)

    def wait_while_running(self, wait_time=0.5):
        while True:
            if self.status != "RUNNING": #TODO: "BSREAD_STILL_RUNNING" ?
                break
            sleep(wait_time)

    @property
    def status(self):
        stat = self.client.get_status()
        stat = stat["status"]
        prefix = "IntegrationStatus."
        if stat.startswith(prefix):
            stat = stat[len(prefix):]
        return stat

    def get_last_pedestal(self):
        return find_last_pedestal(self.active_clients, self.paths.pede)

    def __repr__(self):
        clients = self.active_clients
        clients = ", ".join(clients)
        return "Detector Integration API on {} (status: {})\nClients: {}".format(self.api_address, self.status, clients)



class DIAConfig:

    def __init__(self, instrument, pgroup):
        self.instrument = instrument

        pgroup = str(pgroup)
        if not pgroup.startswith("p"):
            pgroup = "p" + pgroup

        if len(pgroup) != 6:
            msg = "invalid pgroup \"{}\" should have the form \"p12345\"".format(pgroup)
            raise ValueError(msg)

        self.pgroup = pgroup


    def to_dict(self, filename=None, channels=None, n_pulses=100, gain_file=None, pede_file=None, is_HG0=False):
        output_file_jf = output_file_bs = filename

        corrections_preview = bool(pede_file or gain_file)

        instrument = self.instrument
        pgroup = self.pgroup

        user = pgroup[1:]
        uid = int(user)

        now = datetime.now()
        now = str(now)

        exptime = EXPTIME[instrument]

        general_config = {
            "user_id": uid,
            "general/user": user,
            "general/process": __name__,
            "general/created": now,
            "general/instrument": instrument
        }

        bsread_config = {
            "output_file": output_file_bs,
            "channels": channels
        }

        writer_config = {
            "output_file": output_file_jf,
            "n_frames": n_pulses
        }

        backend_config = {
            "n_frames": n_pulses,
            "gain_corrections_filename": gain_file,
            "pede_corrections_filename": pede_file,
            "gain_corrections_dataset": "gains",
            "pede_corrections_dataset": "gains",
            "pede_mask_dataset": "pixel_mask",
            "activate_corrections_preview": corrections_preview,
            "is_HG0": is_HG0,
            "bit_depth": 16
        }

        detector_config = {
            "exptime": exptime,
            "cycles": n_pulses,
            "frames" : 1,
            "timing": "trigger",
            "dr": 16
        }

        if is_HG0:
            detector_config["setbit"] = "0x5d 0" # Switch detector to HG0 mode

        bsread_config.update(general_config)
        writer_config.update(general_config)

        config = {
            "bsread": bsread_config,
            "writer": writer_config,
            "backend": backend_config,
            "detector": detector_config
        }

        return config


    def __repr__(self):
        return printable_dict_of_dicts(self.to_dict())



