from glob import glob
import subprocess
from time import sleep

from yaspin import yaspin
from yaspin.spinners import Spinners

from .brokerconfig import flatten_detectors
from .tools import get_endstation
from .restapi import post_request


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

#    print(f"waiting for {timeout} seconds")
#    tqdm_sleep(timeout)


    while fns_before >= set(glob(pattern)):
        print(set(glob(pattern)))
        sleep(1)
        print("waiting for log file")

    new_fnames = set(glob(pattern)) - fns_before
#    new_fnames = sorted(new_fnames)
    print(f"found {len(new_fnames)} new log files")
#    assert len(new_fnames) == 1
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



