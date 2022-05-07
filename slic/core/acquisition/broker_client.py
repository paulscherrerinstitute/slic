import requests
from glob import glob
from time import sleep
from yaspin import yaspin
from yaspin.spinners import Spinners
import numpy as np

from slic.utils import xrange, tqdm_mod, tqdm_sleep
from slic.utils import json_validate

from .broker_tools import get_current_pulseid


class BrokerClient:

    def __init__(self, *args, address="http://sf-daq:10002", wait_time=0.1, **kwargs):
        self.config = BrokerConfig(*args, **kwargs)
        self.address = address
        self.wait_time = wait_time

        self.set_config(0, None) #TODO: sensible defaults?

        self.running = False
        self.running_continuously = False
        self.run_number = None


    def set_config(self, n_pulses, *args, timeout=10, **kwargs):
        self.n_pulses = n_pulses
        self.timeout = timeout
        self.config.set(*args, **kwargs)

    def get_config(self, *args):
        return self.config.to_dict(*args)


    def start(self):
        current_pulseid = get_current_pulseid()
        n_pulses = self.n_pulses
        rate_multiplicator = self.config.rate_multiplicator

        start_pulseid, n_pulses_actual = aligned_pid_and_n(current_pulseid, n_pulses, rate_multiplicator)

        res = self.run(start_pulseid, n_pulses_actual)
        return res


    def start_continuous(self, n_repeat=None):
        current_pulseid = get_current_pulseid()
        n_pulses = self.n_pulses
        rate_multiplicator = self.config.rate_multiplicator

        start_pulseid = align_pid_left(current_pulseid, rate_multiplicator)

        res = list(self.run_continuous(start_pulseid, n_pulses, n_repeat=n_repeat))
        return res


    def run_continuous(self, start_pulseid, n_pulses, n_repeat=None):
        self.running_continuously = True

        for i in xrange(n_repeat):
            #TODO: for debugging
            counter = f"#{i+1}"
            if n_repeat:
                counter += f" / {n_repeat}"
            stop_pulseid = start_pulseid + n_pulses
            print(counter, start_pulseid, stop_pulseid, n_pulses)

            yield self.run(start_pulseid, n_pulses)

            if not self.running_continuously:
                break

            start_pulseid += n_pulses + 1 #TODO: check whether upper boundary is excluded (otherwise no +1 here)

        self.running_continuously = False


    def run(self, start_pulseid, n_pulses):
        assert self.run_number is not None, "current run number is None" #TODO: raise proper exception

        # n_pulses may differ from self.n_pulses due to alignment
        # there is no alignment done in here, except for early stops
        stop_pulseid = start_pulseid + n_pulses

        current_pulseid = get_current_pulseid()
        rate_multiplicator = self.config.rate_multiplicator

        self.running = True

        with tqdm_mod(total=n_pulses) as pbar:
            while self.running:
                current_pulseid = get_current_pulseid()
                delta_n = (current_pulseid - start_pulseid) // rate_multiplicator
                pbar.set(delta_n)
                if current_pulseid > stop_pulseid:
                    break
                sleep(self.wait_time)

        if not self.running: # stopped early
            stop_pulseid = current_pulseid
            stop_pulseid = align_pid_right(stop_pulseid, rate_multiplicator)

        self.running = False

        params = self.get_config(self.run_number, start_pulseid, stop_pulseid)
        res = retrieve(self.address, params, timeout=self.timeout)

        run_number = res["run_number"]
        assert run_number == self.run_number, f"received {run_number} and expected {self.run_number} run numbers not identical" #TODO: raise proper exception

        return res


    def stop(self):
        self.running = False
        self.running_continuously = False


    def next_run(self):
        self.run_number = run_number = advance_run_number(self.address, self.config.pgroup)
        return run_number


    @property
    def status(self):
        if self.running:
            return "running"
        if self.running_continuously:
            return "running continuously"
        return "idle"


    #TODO: this needs work
    def take_pedestal(self, detectors=None, rate=None):
        if detectors is None:
            detectors = self.config.detectors

        if not detectors:
            raise ValueError(f"Need at least one detector to take pedestal (got: {detectors})")

        detectors = flatten_detectors(detectors)

        if rate is None:
            rate_multiplicator = self.config.rate_multiplicator
        else:
            rate_multiplicator = int(round(100. / rate))

        pgroup = self.config.pgroup

        params = dict(
            detectors=detectors,
            rate_multiplicator=rate_multiplicator,
            pgroup=pgroup
        )


        n_pulses = 5000 # this is a constant on the broker side
        timeout = 10 + n_pulses / 100 * rate_multiplicator

        requrl = self.address.rstrip("/") + "/take_pedestal"
        print("posting:", requrl, params)
        response = post_request(requrl, params, timeout)
        print("done, got:", response)

        print(f"waiting for {timeout} seconds")
        tqdm_sleep(timeout)

        #TODO: follow /sf/{beamline}/data/{pgroup}/raw/run_info/{(run_number//1000*1000):06}/run_{run_number:06}.PEDESTAL.log


        run_number = response["run"]
        padded_run_number = str(run_number).zfill(6)

        fnames_raw = [f"/sf/*/data/{pgroup}/raw/JF_pedestals/run_{padded_run_number}.{det}.h5"     for det in detectors]
        fnames_res = [f"/sf/*/data/{pgroup}/raw/JF_pedestals/run_{padded_run_number}.{det}.res.h5" for det in detectors]
        print(fnames_raw)
        print(fnames_res)
        wait_for_files("raw files", fnames_raw)
        wait_for_files("res files", fnames_res)

        print("done :)")
        return run_number



def advance_run_number(address, pgroup, *args, **kwargs):
    params = {"pgroup": pgroup}
    requrl = address.rstrip("/") + "/get_next_run_number"
    response = get_request(requrl, params, *args, **kwargs)
    run_number = response["message"]
    run_number = int(run_number)
    return run_number


def get_run_number(address, pgroup, *args, **kwargs):
    params = {"pgroup": pgroup}
    requrl = address.rstrip("/") + "/get_last_run_number"
    response = get_request(requrl, params, *args, **kwargs)
    run_number = response["message"]
    run_number = int(run_number)
    return run_number


def retrieve(address, *args, **kwargs):
    requrl = address.rstrip("/") + "/retrieve_from_buffers"
    response = post_request(requrl, *args, **kwargs)
    res = dict(
        run_number       = int(response["run_number"]),
        acq_number       = int(response["acquisition_number"]),
        total_acq_number = int(response["unique_acquisition_number"]),
        filenames = response["files"]
    )
    return res


def post_request(requrl, params, timeout=10):
    params = json_validate(params)
    response = requests.post(requrl, json=params, timeout=timeout).json()
    return validate_response(response)

def get_request(requrl, params, timeout=10):
    params = json_validate(params)
    response = requests.get(requrl, json=params, timeout=timeout).json()
    return validate_response(response)


def validate_response(resp):
    if resp.get("status") == "ok":
        return resp

    message = resp.get("message", "Unknown error")
    msg = "An error happened on the server:\n{}".format(message)
    raise BrokerError(msg)



class BrokerError(Exception):
    pass



class BrokerConfig:

    def __init__(self, pgroup, rate_multiplicator=1, append_user_tag_to_data_dir=False, client_name=None):
        self.pgroup = pgroup
        self.rate_multiplicator = rate_multiplicator #TODO: can we read that from epics?
        self.append_user_tag_to_data_dir = append_user_tag_to_data_dir
        self.client_name = client_name
        self.set(None) #TODO: sensible defaults?

    def set(self, output_dir, detectors=None, channels=None, pvs=None, scan_info=None):
        self.output_dir = output_dir
        self.detectors = detectors
        self.channels = channels
        self.pvs = pvs
        self.scan_info = scan_info


    def to_dict(self, run_number, start_pulseid, stop_pulseid):
        config = {
            "pgroup": self.pgroup,
            "rate_multiplicator": self.rate_multiplicator,
            "append_user_tag_to_data_dir": self.append_user_tag_to_data_dir,
#            "directory_name": self.output_dir, # structure <= 2021
            "user_tag": self.output_dir,        # structure >= 2022
            "run_number": run_number,           # new in 2022
            "start_pulseid": start_pulseid,
            "stop_pulseid": stop_pulseid
        }

        if self.client_name:
            config["client_name"] = self.client_name

        detectors = self.detectors
        if detectors:
            detectors = flatten_detectors(detectors)
            config["detectors"] = detectors

        if self.channels:
            bsread_channels, camera_channels = split_channels(self.channels)
            if bsread_channels:
                config["channels_list"] = bsread_channels
            if camera_channels:
                config["camera_list"] = camera_channels

        if self.pvs:
            config["pv_list"] = self.pvs

        if self.scan_info:
            config["scan_info"] = self.scan_info

        return config



def split_channels(channels):
    bsread_channels = []
    camera_channels = []
    for c in channels:
        if c.endswith(":FPICTURE"):
            camera_channels.append(c)
        else:
            bsread_channels.append(c)

    return bsread_channels, camera_channels



def flatten_detectors(dets):
    if isinstance(dets, dict):
        return harmonize_detector_dict(dets)

    if isinstance(dets, (list, tuple)):
        res = {}
        for d in dets:
            if isinstance(d, dict):
                d = harmonize_detector_dict(d)
                res.update(d)
            elif isinstance(d, str):
                res[d] = {} # defaults via empty dict
            else:
                raise ValueError(f"Cannot interpret \"{d}\" as detector")
        return res

    raise ValueError(f"Cannot interpret \"{dets}\" as detector(s)")


def harmonize_detector_dict(d):
    if "name" in d:
        name = d["name"]
        d = {
            name: {
                k: v for k, v in d.items() if k != "name"
            }
        }
    return d



def aligned_pid_and_n(start, n, rm):
    start, stop = aligned_pids(start, n, rm)
    return start, stop - start

def aligned_pids(start, n, rm):
    """
    return start/stop pids aligned to rep rate
    """
#    start -= 1 #TODO: count from zero?
    block_start = (start // rm) + 1 # calc block where start is in, then take following block
    block_stop  = block_start + n
    start = block_start * rm # adjust to actual rep rate (example: recording is at 100 Hz; for a 50 Hz device, 2*n pulses need to be recorded to get n pulses with that device)
    stop  = block_stop  * rm #TODO: check whether upper boundary is excluded (otherwise -1 here)
    return int(start), int(stop)


def align_pid_left(pid, rm):
    return align_pid(pid, rm, 0)

def align_pid_right(pid, rm):
    return align_pid(pid, rm, 1)

def align_pid(pid, rm, block_offset=0):
    block = pid // rm
    block += block_offset
    return block * rm



def wait_for_files(label, fnames):
    with yaspin(Spinners.clock, text=f"elapsed time: {label}", timer=True) as sp:
        while True:
            all_exists = all(bool(glob(fn)) for fn in fnames)
            if all_exists:
                break
            sleep(10)
        sp.ok("✅")



