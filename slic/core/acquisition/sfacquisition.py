import os
from time import sleep
from collections import defaultdict

from slic.utils.channels import Channels
from slic.utils.printing import printable_dict
from slic.core.task import DAQTask

from .baseacquisition import BaseAcquisition
from .sfpaths import SwissFELPaths
from .bschannels import BSChannels

from .broker_client import BrokerClient


class SFAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup, default_data_base_dir="static_data", default_detectors=None, default_channels=None, default_pvs=None, api_address="http://sf-daq:10002", rate_multiplicator=1, append_user_tag_to_data_dir=False):
        self.instrument = instrument
        self.default_data_base_dir = default_data_base_dir

        if not default_channels:
            paths = SwissFELPaths(instrument, pgroup)
            default_channels = BSChannels.from_file(paths.default_channel_list)

        self.default_detectors = default_detectors
        self.default_channels = default_channels
        self.default_pvs = default_pvs

        self.client = BrokerClient(pgroup, address=api_address, rate_multiplicator=rate_multiplicator, append_user_tag_to_data_dir=append_user_tag_to_data_dir, client_name="slic")

        self.current_task = None


    def acquire(self, filename, data_base_dir=None, detectors=None, channels=None, pvs=None, scan_info=None, n_pulses=100, continuous=False, is_scan_step=False, wait=True):
        if not is_scan_step:
            run_number = self.client.next_run()
            print(f"Advanced run number to {run_number}.")
        else:
            run_number = self.client.run_number
            print(f"Continuing run number {run_number}.")

        if not filename or filename == "/dev/null":
            print("Skipping retrieval since no filename was given.")
            return

#TODO: this is not supported by sf_daq anymore; need a replacement?
#        if data_base_dir is None:
#            print("No base directory specified, using default base directory.")
#            data_base_dir = self.default_data_base_dir

#        filename = os.path.join(data_base_dir, filename)

        if detectors is None:
            print("No detectors specified, using default detector list.")
            detectors = self.default_detectors

        if pvs is None:
            print("No PVs specified, using default PV list.")
            pvs = self.default_pvs

        if channels is None:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        bschs = BSChannels(*channels)
        bschs.check()

        client = self.client
        client.set_config(n_pulses, filename, detectors=detectors, channels=channels, pvs=pvs, scan_info=scan_info)

        paths = SwissFELPaths(self.instrument, self.pgroup)

        def _acquire():
            res = client.start_continuous() if continuous else client.start()
            res = transpose_dicts(res) #TODO: only for continuous?
            filenames = res.pop("filenames")
            print_response(res)
            return filenames

        task = DAQTask(_acquire, stopper=client.stop, filename=filename, hold=False)
        self.current_task = task

        if wait:
            try:
                task.wait()
            except KeyboardInterrupt:
                print("Stopped current DAQ task:")

        return task


    @property
    def pgroup(self):
        return self.client.config.pgroup

    @pgroup.setter
    def pgroup(self, value):
        self.client.config.pgroup = value


    @property
    def status(self):
        return self.client.status

    def __repr__(self):
        return "SF DAQ on {} (status: {}, last run: {})".format(self.client.address, self.client.status, self.client.run_number)





def transpose_dicts(seq_of_dicts):
    if isinstance(seq_of_dicts, dict):
        seq_of_dicts = [seq_of_dicts]
    res = defaultdict(list)
    for d in seq_of_dicts:
        for k, v in d.items():
            try:
                res[k].extend(v)
            except TypeError:
                res[k].append(v)
    return dict(res)



def print_response(res):
    to_print = {}
    for k, v in res.items():
        k = k.replace("_", " ")
        if len(set(v)) == 1:
            v = v[0]
        else:
            k = k if k.endswith("s") else k+"s"
        to_print[k] = v

    print(printable_dict(to_print, sorter=None))



