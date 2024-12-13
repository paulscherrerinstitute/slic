import os
from time import sleep
from detector_integration_api import DetectorIntegrationClient

from slic.utils.channels import Channels
from slic.utils import can_create_all_files
from slic.core.task import DAQTask

from .baseacquisition import BaseAcquisition
from .diaconfig import DIAConfig, EXPTIME
from .sfpaths import SwissFELPaths
from .pedestals import find_last_pedestal, take_pedestal


class DIAAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup, default_data_base_dir="static_data", default_channels=None, default_dir=None, api_address=None):
        self.instrument = instrument
        self.pgroup = pgroup
        self.default_data_base_dir = default_data_base_dir

        self.config = DIAConfig(instrument, pgroup)
        self.paths = SwissFELPaths(instrument, pgroup)

        if not default_channels:
            default_channel_list = self.paths.default_channel_list
            default_channels = Channels(default_channel_list)

        if not default_dir:
            default_dir = self.paths.raw

        self.default_channels = default_channels
        self.default_dir = default_dir

        if not api_address:
            api_address = f"http://sf-daq-{instrument}:10000"

        self.api_address = api_address
        self.client = DetectorIntegrationClient(api_address)

        self.current_task = None


    def acquire(self, filename=None, data_base_dir=None, channels=None, n_pulses=100, use_default_dir=True, is_HG0=False, wait=True):
        if not filename:
            filename = "/dev/null"
        else:
            if data_base_dir is None:
                print("No base directory specified, using default base directory.")
                data_base_dir = self.default_data_base_dir
            filename = os.path.join(data_base_dir, filename)

            if use_default_dir:
                filename = os.path.join(self.default_dir, filename)

            filenames = self.make_all_filenames(filename)
            if not can_create_all_files(filenames):
                return

        if channels is None:
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

        task = DAQTask(_acquire, stopper=self.client.stop, filenames=filenames, hold=False)
        self.current_task = task

        if wait:
            try:
                task.wait()
            except KeyboardInterrupt:
                print("Stopped current DAQ task:")

        return task


    def make_all_filenames(self, base):
        res = []
        for client in self.active_clients:
            client = client.upper()
            fn = f"{base}.{client}.h5"
            res.append(fn)
        return res

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

    def take_pedestal(self, analyze=True, n_pulses=1000, n_bad_modules=0, freq=25, user=None):
        instrument = self.instrument
        pgroup = self.pgroup
        api_address = self.api_address
        raw_dir = self.paths.raw
        res_dir = self.paths.res
        exptime = EXPTIME[instrument]
        return take_pedestal(instrument, pgroup, api_address, raw_dir, res_dir, analyze, n_pulses, n_bad_modules, freq, exptime, user)

    def __repr__(self):
        clients = self.active_clients
        clients = ", ".join(clients)
        return f"Detector Integration API on {self.api_address} (status: {self.status})\nClients: {clients}"



