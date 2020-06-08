import requests
from time import sleep
from tqdm import tqdm

from .broker_tools import get_current_pulseid


class BrokerClient:

    def __init__(self, *args, address="http://sf-daq-1:10002", **kwargs):
        self.config = BrokerConfig(*args, **kwargs)
        self.address = address

#TODO begin start/stop logic / needs refactor!

        self.running = False
        self.n_pulses = 0
        self.args = []
        self.kwargs = {}
        self.run_number = None


    def set_config(self, n_pulses, *args, **kwargs):
        self.n_pulses = n_pulses
        self.args = args
        self.kwargs = kwargs


    def start(self):
        start_pulseid = current_pulseid = get_current_pulseid()
        stop_pulseid = start_pulseid + self.n_pulses

        self.running = True

        with tqdm(total=self.n_pulses) as pbar:
            while self.running:
                current_pulseid = get_current_pulseid()
                if current_pulseid > stop_pulseid:
                    break
                sleep(0.1)
                pbar.update(current_pulseid - start_pulseid - pbar.n)

        self.running = False

        stop_pulseid = current_pulseid # in case we stopped early
        self.run_number = self.retrieve(*self.args, start_pulseid, stop_pulseid, **self.kwargs)
        return self.run_number


    def stop(self):
        self.running = False


    @property
    def status(self):
        if self.running:
            return "running"
        else:
            return "idle"


#TODO end start/stop logic


    def retrieve(self, *args, timeout=10, **kwargs):
        requrl = self.address.rstrip("/") + "/retrieve_from_buffers"
        params = self.config.to_dict(*args, **kwargs)
        response = requests.post(requrl, json=params, timeout=timeout).json()
        return validate_response(response)



def validate_response(resp):
    if resp.get("status") == "ok":
        return resp.get("message")

    message = resp.get("message", "Unknown error")
    msg = "An error happened on the server:\n{}".format(message)
    raise BrokerError(msg)



class BrokerError(Exception):
    pass



class BrokerConfig:

    def __init__(self, pgroup, rate_multiplicator=1):
        self.pgroup = pgroup
        self.rate_multiplicator = rate_multiplicator


    def to_dict(self, output_dir, start_pulseid, stop_pulseid, detectors=None, channels=None, pvs=None, scan_info=None):
        config = {
            "pgroup": self.pgroup,
            "rate_multiplicator": self.rate_multiplicator,
            "directory_name": output_dir,
            "start_pulseid": start_pulseid,
            "stop_pulseid": stop_pulseid,
        }

        if detectors:
            detectors = {d: {} for d in detectors} # currently the dicts are empty, thus allow giving just a list as argument
            config["detectors"] = detectors

        if channels:
            bsread_channels, camera_channels = split_channels(channels)
            if bsread_channels:
                config["channels_list"] = bsread_channels
            if camera_channels:
                config["camera_list"] = camera_channels

        if pvs:
            config["pv_list"] = pvs

        if scan_info:
            config["scan_info"] = scan_info

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



