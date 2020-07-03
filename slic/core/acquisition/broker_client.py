import requests
from time import sleep
from tqdm import tqdm

from .broker_tools import get_current_pulseid


class BrokerClient:

    def __init__(self, *args, address="http://sf-daq-1:10002", wait_time=0.1, **kwargs):
        self.config = BrokerConfig(*args, **kwargs)
        self.address = address
        self.wait_time = wait_time

        self.set_config(0, None) #TODO: sensible defaults?

        self.running = False
        self.run_number = None


    def set_config(self, n_pulses, *args, timeout=10, **kwargs):
        self.n_pulses = n_pulses
        self.timeout = timeout
        self.config.set(*args, **kwargs)

    def get_config(self, *args):
        return self.config.to_dict(*args)


    def start(self):
        n_pulses = self.n_pulses
        rate_multiplicator = self.config.rate_multiplicator

        current_pulseid = get_current_pulseid()
        start_pulseid, stop_pulseid = aligned_pids(current_pulseid, n_pulses, rate_multiplicator)

        self.running = True

        with stqdm(total=n_pulses) as pbar:
            while self.running:
                current_pulseid = get_current_pulseid()
                if current_pulseid > stop_pulseid:
                    break
                sleep(self.wait_time)
                delta_n = (current_pulseid - start_pulseid) // rate_multiplicator
                pbar.set(delta_n)

        if not self.running: # stopped early
            stop_pulseid = current_pulseid
            stop_pulseid = align_pid_right(stop_pulseid, rate_multiplicator)

        self.running = False

        params = self.get_config(start_pulseid, stop_pulseid)
        self.run_number = retrieve(self.address, params, timeout=self.timeout)
        return self.run_number


    def stop(self):
        self.running = False


    @property
    def status(self):
        if self.running:
            return "running"
        return "idle"



def retrieve(address, *args, **kwargs):
    requrl = address.rstrip("/") + "/retrieve_from_buffers"
    response = post_request(requrl, *args, **kwargs)
    runnumber = int(response)
    return runnumber


def post_request(requrl, params, timeout=10):
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
        self.rate_multiplicator = rate_multiplicator #TODO: can we read that from epics?
        self.set(None) #TODO: sensible defaults?

    def set(self, output_dir, detectors=None, channels=None, pvs=None, scan_info=None):
        self.output_dir = output_dir
        self.detectors = detectors
        self.channels = channels
        self.pvs = pvs
        self.scan_info = scan_info


    def to_dict(self, start_pulseid, stop_pulseid):
        config = {
            "pgroup": self.pgroup,
            "rate_multiplicator": self.rate_multiplicator,
            "directory_name": self.output_dir,
            "start_pulseid": start_pulseid,
            "stop_pulseid": stop_pulseid
        }

        if self.detectors:
            detectors = {d: {} for d in self.detectors} # currently the dicts are empty, thus allow giving just a list as argument
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



class stqdm(tqdm):

    def set(self, elapsed):
        """
        update with elapsed n, i.e., the delta between start and current n
        """
        elapsed = clamp(elapsed, 0, self.total)
        increment = elapsed - self.n
        self.update(increment)



def clamp(val, vmin, vmax):
    val = max(val, vmin)
    val = min(val, vmax)
    return val



