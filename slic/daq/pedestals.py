import os
from glob import glob
from datetime import datetime
from collections import defaultdict


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










def take_pedestal(self, n_frames, analyze=True, n_bad_modules=0, update_config=True, freq=25):
    from jungfrau_utils.scripts.jungfrau_run_pedestals import run as jungfrau_utils_run
    directory = "/sf/%s/data/p%d/raw/JF_pedestals/" % (self.instrument, self.pgroup)
    if not os.path.exists(directory):
        print("Directory %s not existing, AND I CAN NOT CREATE IT, CALL DIMA" % directory)
        #os.makedirs(directory)

    res_dir = directory.replace("/raw/", "/res/")
    if not os.path.exists(res_dir):
        print("Directory %s not existing, creating it" % res_dir)
        os.makedirs(res_dir)
        os.chmod(res_dir, 0o775)
    filename = "pedestal_%s" % datetime.now().strftime("%Y%m%d_%H%M")
    period = 1 / freq
    jungfrau_utils_run(self.api_address, filename, directory, self.pgroup, period, self.detector_config["exptime"],
                                 n_frames, 1, analyze, n_bad_modules, self.instrument)

    if update_config:
        self.pede_file = (directory + filename).replace("raw/", "res/").replace(".h5", ".res.h5")
        print("Pedestal file updated to %s" % self.pede_file)
    return self.pede_file

#TODO: ?!?
    if analyze:
        pedestals_taken = Path(directory).glob(filename + "*")
        print(
            "Analysis of pedestal data is outsourced to batch farm, user credentials required."
        )
        user = input("enter user name for analysis on sf batch farm: ")
        commandstr = [
            f"ssh {user}@sf-cn-1 source /sf/{self.instrument}/bin/anaconda_env"
        ]
        for ped in pedestals_taken:
            commandstr.append(
                f"sbatch jungfrau_create_pedestals --filename {ped.as_posix()} --directory {res_dir} --verbosity 4"
            )
        os.system("\;".join(commandstr))














