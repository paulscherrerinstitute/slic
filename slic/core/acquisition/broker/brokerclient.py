from time import sleep, time

from slic.utils import forwards_to, xrange, tqdm_mod#, tqdm_sleep

from .restapi import RESTAPI
from .brokerconfig import BrokerConfig, flatten_detectors
from .pedestal import take_pedestal
from .pids import align_pid_left, align_pid_right, aligned_pid_and_n
from .tools import get_current_pulseid
from .poweron import guided_power_on
from .jfstatus import color_bar


class BrokerClient:

    def __init__(self, *args, address=None, host="sf-daq", port=10002, wait_time=0.1, **kwargs):
        #TODO: remove this check once migrated everywhere
        if address is not None:
            raise DeprecationWarning("address is deprecated, use host and port instead")

        self.config = BrokerConfig(*args, **kwargs)
        self.wait_time = wait_time

        self.restapi = RESTAPI(host=host, port=port)

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


    def get_config_pvs(self, *args, **kwargs):
        return self.restapi.get_config_pvs(*args, **kwargs)

    def set_config_pvs(self, pvs, *args, **kwargs):
        return self.restapi.set_config_pvs(pvs, *args, **kwargs)


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
        res = self.restapi.retrieve(params, timeout=self.timeout)

        run_number = res["run_number"]
        assert run_number == self.run_number, f"received {run_number} and expected {self.run_number} run numbers not identical" #TODO: raise proper exception

        return res


    def stop(self):
        self.running = False
        self.running_continuously = False


    def next_run(self, *args, **kwargs):
        self.run_number = run_number = self.restapi.advance_run_number(self.config.pgroup, *args, **kwargs)
        return run_number


    def __repr__(self):
        return f"SF DAQ (status: {self.status}, last run: {self.run_number})\n{self.restapi}"


    @property
    def status(self):
        if self.running:
            return "running"
        if self.running_continuously:
            return "running continuously"
        return "idle"


    def take_pedestal(self, detectors=None, rate=None, pedestalmode=False):
        take_pedestal(self.restapi, self.config, detectors=detectors, rate=rate, pedestalmode=pedestalmode)


    def power_on(self, detectors=None, wait=False, wait_time=0.1, timeout=300, **kwargs):
        if detectors is None:
            detectors = self.config.detectors

        if not detectors:
            raise ValueError(f"Need at least one detector to power on (got: {detectors})")

        detectors = flatten_detectors(detectors)
        for d in detectors:
            msg = self.restapi.power_on_detector(d, **kwargs)
            print(f"{d}: {msg}")

        if not wait:
            return

        detector = list(detectors.keys())[0] #TODO
        self.wait_for_status(detector, wait_time=wait_time, timeout=timeout)


    def wait_for_status(self, detector, status="running", wait_time=0.1, timeout=300):
        start_time = time()
        stop_time = start_time + timeout

        while True:
            status_reply = self.restapi.get_detector_status(detector)

            cb = color_bar(status_reply)
            print(f"{detector}: {cb}")

            if status in status_reply:
                break

            if time() > stop_time:
                print(f'{detector}: waiting for "{status}" status timed out')
                break

            sleep(wait_time)


    @forwards_to(guided_power_on, nfilled=1)
    def guided_power_on(self, *args, **kwargs):
        guided_power_on(self, *args, **kwargs)



