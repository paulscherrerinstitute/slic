from glob import glob
import subprocess

from time import sleep
from yaspin import yaspin
from yaspin.spinners import Spinners

from slic.utils import xrange, tqdm_mod#, tqdm_sleep

from .brokerconfig import BrokerConfig, flatten_detectors
from .pids import aligned_pid_and_n, align_pid_left, align_pid_right
from .tools import get_current_pulseid, get_endstation
from .restapi import advance_run_number, post_request, retrieve, get_config_pvs, set_config_pvs


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
        return get_config_pvs(self.address, *args, **kwargs)

    def set_config_pvs(self, pvs, *args, **kwargs):
        return set_config_pvs(self.address, pvs, *args, **kwargs)


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


    def next_run(self, *args, **kwargs):
        self.run_number = run_number = advance_run_number(self.address, self.config.pgroup, *args, **kwargs)
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


        instrument = get_endstation()
        pattern = f"/sf/{instrument}/data/{pgroup}/raw/JF_pedestals/*.log"
        fns_before = set(glob(pattern))


        n_pulses = 5000 # this is a constant on the broker side
        timeout = 10 + n_pulses / 100 * rate_multiplicator

        print("posting:", params)
        response = post_request(self.address, "take_pedestal", params, timeout=timeout)
        print("done, got:", response)

#        print(f"waiting for {timeout} seconds")
#        tqdm_sleep(timeout)


        while fns_before >= set(glob(pattern)):
            print(set(glob(pattern)))
            sleep(1)
            print("waiting for log file")

        new_fnames = set(glob(pattern)) - fns_before
#        new_fnames = sorted(new_fnames)
        print(f"found {len(new_fnames)} new log files")
#        assert len(new_fnames) == 1
        new_fname = new_fnames.pop()
        print(new_fname)

        print()
        print("tailing log file:")
        print("-" * 100)

        f = subprocess.Popen(["tail", "-F", new_fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with yaspin(Spinners.soccerHeader, timer=True) as sp:
            while True:
                line = f.stdout.readline()
                line = line.decode("utf-8").rstrip()
                print("\n" + line)
                if "processing request took " in line and " seconds" in line:
                    f.kill()
                    break
            sp.ok("🥅")

        print("-" * 100)
        print("end of log")
        print()

        prefix = new_fname.split("/")[-1].split(".")[0]

        fnames_raw = [f"/sf/{instrument}/data/{pgroup}/raw/JF_pedestals/{prefix}.{det}.h5"     for det in detectors]
        fnames_res = [f"/sf/{instrument}/data/{pgroup}/raw/JF_pedestals/{prefix}.{det}.res.h5" for det in detectors]
        print(fnames_raw)
        print(fnames_res)
        wait_for_files("raw files", fnames_raw)
        wait_for_files("res files", fnames_res)

        print("done 🏟️")
        return new_fname



def wait_for_files(label, fnames):
    with yaspin(Spinners.clock, text=f"elapsed time: {label}", timer=True) as sp:
        while True:
            all_exists = all(bool(glob(fn)) for fn in fnames)
            if all_exists:
                break
            sleep(10)
        sp.ok("✅")



