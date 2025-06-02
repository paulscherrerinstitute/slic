from collections import defaultdict
import numpy as np

#from slic.utils.channels import Channels
from slic.utils.printing import printable_dict
from slic.core.task import DAQTask

from .baseacquisition import BaseAcquisition
from .sfpaths import SwissFELPaths
from .bschannels import BSChannels

from .broker import BrokerClient, align_pid_left, align_pid_right
from .detcfg import DetectorConfig

#TODO: install pika everywhere and remove the following
# handle cases where pika is not available
try:
    from .broker.requeststatus import RequestStatus
except ImportError:
    RequestStatus = None


class SFAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup, default_data_base_dir="static_data", default_detectors=None, default_channels=None, default_pvs=None, api_address=None, api_host="sf-daq", api_port=10002, rate_multiplicator=1, append_user_tag_to_data_dir=False, spreadsheet=None, **kwargs):
        #TODO: remove this check once migrated everywhere
        if api_address is not None:
            raise DeprecationWarning("api_address is deprecated, use api_host and api_port instead")

        self.instrument = instrument
        self.default_data_base_dir = default_data_base_dir
        self.spreadsheet = spreadsheet

        if not default_channels:
            paths = SwissFELPaths(instrument, pgroup)
            default_channels = BSChannels.from_file(paths.default_channel_list)

        #TODO: convert here?
        if not isinstance(default_detectors, DetectorConfig):
            default_detectors = DetectorConfig(default_detectors)

        self.default_detectors = default_detectors
        self.default_channels  = default_channels
        self.default_pvs       = default_pvs

        self.client = BrokerClient(pgroup, host=api_host, port=api_port, rate_multiplicator=rate_multiplicator, append_user_tag_to_data_dir=append_user_tag_to_data_dir, client_name="slic", **kwargs)

        #TODO: install pika everywhere and remove the following
        # handle cases where pika is not available
        if RequestStatus is None:
            self.status = None
        else:
            self.status = RequestStatus(instrument=instrument, host=api_host)

        self.current_task = None


    def acquire(self, filename, data_base_dir=None, detectors=None, channels=None, pvs=None, scan_info=None, n_pulses=100, n_repeat=1, is_scan_step=False, wait=True, **kwargs):
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
        client.set_config(n_pulses, filename, detectors=detectors, channels=channels, pvs=pvs, scan_info=scan_info, **kwargs)

#        paths = SwissFELPaths(self.instrument, self.pgroup)

        def _acquire():
            if not is_scan_step:
                if self.spreadsheet is not None:
                    self.spreadsheet.add(run_number, filename, n_pulses)
            res = client.start() if n_repeat == 1 else client.start_continuous(n_repeat=n_repeat)
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



    #TODO: only a first try
    def retrieve(self, filename, pulseids, run_number=None, **kwargs):
        start_pulseid = min(pulseids)
        stop_pulseid  = max(pulseids)

        client = self.client

        rate_multiplicator = client.config.rate_multiplicator
        start_pulseid = align_pid_left(start_pulseid, rate_multiplicator)
        stop_pulseid = align_pid_right(stop_pulseid, rate_multiplicator)

        client.config.set(filename, detectors=self.default_detectors, channels=self.default_channels, pvs=self.default_pvs, **kwargs)

        if run_number is None:
            run_number = client.next_run()

        params = client.get_config(run_number, start_pulseid, stop_pulseid)

        if not is_continuous(pulseids):
            params["selected_pulse_ids"] = pulseids

        res = self.client.restapi.retrieve(params, timeout=client.timeout)

        res_run_number = res["run_number"]
        assert res_run_number == run_number, f"received {res_run_number} and expected {run_number} run numbers not identical"

#        res = transpose_dicts(res)
#        filenames = res.pop("filenames")
#        print_response(res)

        return res



    @property
    def pgroup(self):
        return self.client.config.pgroup

    @pgroup.setter
    def pgroup(self, value):
        self.client.config.pgroup = value


    def __repr__(self):
        return repr(self.client)


    def get_config_pvs(self):
        return self.client.get_config_pvs()

    def set_config_pvs(self, pvs=None):
        if pvs is None:
            pvs = self.default_pvs
        return self.client.set_config_pvs(pvs)

    def update_config_pvs(self, pvs=None, force=False):
        if pvs is None:
            pvs = self.default_pvs
        current = self.get_config_pvs()
        pvs = set(pvs)
        current = set(current)
        merged = pvs | current
        if not force and merged == pvs:
            return
        merged = sorted(merged)
        return self.client.set_config_pvs(merged)

    def diff_config_pvs(self, pvs=None):
        if pvs is None:
            pvs = self.default_pvs
        current = self.get_config_pvs()
        only_remote = set(current) - set(pvs)
        only_local  = set(pvs) - set(current)
        return {"only remote": sorted(only_remote), "only local": sorted(only_local)}



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



def is_continuous(arr, step=1):
    udeltas = np.unique(np.diff(arr))
    return np.array_equal(udeltas, [step])



