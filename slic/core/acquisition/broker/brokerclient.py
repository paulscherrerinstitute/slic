from time import sleep

from slic.utils import xrange, tqdm_mod#, tqdm_sleep

from . import restapi
from .brokerconfig import BrokerConfig, flatten_detectors
from .pedestal import take_pedestal
from .pids import align_pid_left, align_pid_right, aligned_pid_and_n
from .tools import get_current_pulseid


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


    def get_config_pvs(self, *args, **kwargs):
        return restapi.get_config_pvs(self.address, *args, **kwargs)

    def set_config_pvs(self, pvs, *args, **kwargs):
        return restapi.set_config_pvs(self.address, pvs, *args, **kwargs)


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
        res = restapi.retrieve(self.address, params, timeout=self.timeout)

        run_number = res["run_number"]
        assert run_number == self.run_number, f"received {run_number} and expected {self.run_number} run numbers not identical" #TODO: raise proper exception

        return res


    def stop(self):
        self.running = False
        self.running_continuously = False


    def next_run(self, *args, **kwargs):
        self.run_number = run_number = restapi.advance_run_number(self.address, self.config.pgroup, *args, **kwargs)
        return run_number


    def __repr__(self):
        return f"SF DAQ on {self.address} (status: {self.status}, last run: {self.run_number})"


    @property
    def status(self):
        if self.running:
            return "running"
        if self.running_continuously:
            return "running continuously"
        return "idle"


    def take_pedestal(self, detectors=None, rate=None, pedestalmode=False):
        take_pedestal(self.address, self.config, detectors=detectors, rate=rate, pedestalmode=pedestalmode)


    def power_on(self, detectors=None, **kwargs):
        if detectors is None:
            detectors = self.config.detectors

        if not detectors:
            raise ValueError(f"Need at least one detector to power on (got: {detectors})")

        detectors = flatten_detectors(detectors)
        for d in detectors:
            msg = restapi.power_on_detector(self.address, d, **kwargs)
            print(f"{d}: {msg}")



