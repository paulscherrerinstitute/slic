import os
from glob import glob
from datetime import datetime
from collections import defaultdict
from jungfrau_utils.scripts.jungfrau_run_pedestals import run as ju_record_raw_pedestal



TIMESTAMP_FORMAT = "%Y%m%d_%H%M"



def find_last_pedestal(clients, directory="."):
    clients = set(clients)
    clients = clients - {"bsread"}

    pede_pattern = os.path.join(directory, "pedestal_*.res.h5")
    pede_files = glob(pede_pattern)

    found = defaultdict(set)
    for fn in pede_files:
        ts = extract_timestamp(fn)
        det = extract_detector(fn)
        found[ts].add(det)

    good = set()
    for ts, dets in found.items():
        if clients.issubset(dets):
            good.add(ts)

    if not good:
        return None

    best = max(good)
    best = best.strftime(TIMESTAMP_FORMAT)

    res = "pedestal_" + best
    res = os.path.join(directory, res)
    return res


def extract_timestamp(fn):
    fn = strip_folder(fn)
    base = fn.split(".")[0]
    prefix = "pedestal_"
    assert base.startswith(prefix), "\"{}\" does not start with \"{}\"".format(base, prefix)
    timestamp = base[len(prefix):]
    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
    return timestamp

def extract_detector(fn):
    fn = strip_folder(fn)
    detector = fn.split(".")[1]
    return detector

def strip_folder(fn):
    return os.path.split(fn)[-1]



def take_pedestal(instrument, pgroup, api_address, raw_dir, res_dir, analyze_locally, n_pulses, n_bad_modules, freq, exptime, user):
    make_missing_dir(raw_dir)
    make_missing_dir(res_dir)

    now = datetime.now().strftime(TIMESTAMP_FORMAT)
    file_base = "pedestal_" + now

    raw_file_base = raw_dir + file_base
    res_file_base = res_dir + file_base

    period = 1 / freq
    trigger = 1

    ju_record_raw_pedestal(api_address, file_base, raw_dir, pgroup, period, exptime, n_pulses, trigger, analyze_locally, n_bad_modules, instrument)

    if not analyze_locally:
        analyze_pedestal_on_cluster(instrument, raw_file_base, res_dir, user)

    return res_file_base


def make_missing_dir(d):
    if os.path.exists(d):
        return

    msg = "Directory \"{}\" does not exist, creating it...".format(d)
    print(msg)

    os.makedirs(d, exist_ok=True)
    os.chmod(d, 0o775)


def analyze_pedestal_on_cluster(instrument, raw_file_base, res_dir, user=None):
    pedestals_taken = raw_file_base + "*"
    pedestals_taken = glob(pedestals_taken)

    if not pedestals_taken:
        return

    if user is None:
        print("Analysis of raw pedestal data on SF computing nodes requires user credentials.")
        user = input("Enter user name: ")

    cmd = f"ssh {user}@sf-cn-1 source /sf/{instrument}/bin/anaconda_env"
    commands = [cmd]

    for ped in pedestals_taken:
        cmd = f"sbatch jungfrau_create_pedestals --filename {ped} --directory {res_dir} --verbosity 4"
        commands.append(cmd)

    cmd = "\;".join(commands)
    os.system(cmd)



