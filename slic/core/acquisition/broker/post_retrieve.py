import json
from functools import partial
from glob import glob

from slic.core.acquisition.broker import restapi
from slic.utils import json_load


API_ADDR = "http://sf-daq:10002"



def post_retrieve(addr, endstation, pgroup, run, acqs=None, continue_run=False):
    """
    post retrieve data from sf-daq
    acqs: sequence of integer acquisition numbers or None (default: all acquisition numbers of the selected run)
    continue_run: append to existing run (default: create new run)
    """
    dir_run_meta = mk_dir_run_meta(endstation, pgroup, run)

    if acqs is None:
        fns = mk_fns_run(dir_run_meta)
    else:
        fns = mk_fns_acqs(dir_run_meta, acqs)

    updates = mk_updates(addr, pgroup, continue_run)

    post_retrieve_fns_acqs(addr, fns, updates)


def mk_dir_run_meta(endstation, pgroup, run):
    pattern = f"/sf/{endstation}/data/{pgroup}/raw/run{run:04}*/meta"
    return single_glob(pattern)

def single_glob(pattern):
    ns = glob(pattern)
    assert len(ns) == 1, ns
    n = ns[0]
    return n


def mk_fns_run(dir_run_meta):
    pattern = f"{dir_run_meta}/acq*.json"
    return sorted(glob(pattern))

def mk_fns_acqs(dir_run_meta, acqs):
    return sorted(mk_fn_acq(dir_run_meta, a) for a in acqs)

def mk_fn_acq(dir_run_meta, acq):
    return f"{dir_run_meta}/acq{acq:04}.json"


def mk_updates(addr, pgroup, continue_run):
    updates = {}
    if not continue_run:
        run_number = restapi.advance_run_number(addr, pgroup)
        updates["run_number"] = run_number
    return updates


def post_retrieve_fns_acqs(addr, fns, updates):
    for fn in fns:
        post_retrieve_fn_acq(addr, fn, updates)

def post_retrieve_fn_acq(addr, fn, updates):
    print("🛠️ working on:", fn)
    req = json_load(fn)
    print("🔎 read original request:", pretty_dict(req))
    if updates:
        print("🖊️ updating request:", pretty_dict(updates))
        req.update(updates)
        print("🪥 new request:", pretty_dict(req))
    resp = restapi.retrieve(addr, req)
    print("💌 response:", pretty_dict(resp))
    print()



def pretty_dict(d):
    return json.dumps(d, indent=4)



class DryRunner:
    """
    wrapper to disable/enable calling methods of wrapped via the dry_run attribute
    """

    def __init__(self, wrapped, dry_run=False):
        self.wrapped = wrapped
        self.dry_run = dry_run

    def __getattr__(self, name):
        if self.dry_run:
            return partial(print, f"🚱 dry run -- skipping: {name}")
        return getattr(self.wrapped, name)


restapi = DryRunner(restapi)





def main():
    import argparse
    import re

    from slic.core.acquisition.broker.tools import SUBNET_TO_ENDSTATION, get_endstation


    endstations = tuple(SUBNET_TO_ENDSTATION.values())
    try:
        endstation = get_endstation()
    except RuntimeError:
        endstation = None


    def validate_pgroup(pgroup):
        pattern = r"^p\d{5}$"
        if re.match(pattern, pgroup):
            return pgroup
        msg = f"invalid pgroup value: {pgroup!r}"
        raise argparse.ArgumentTypeError(msg)


    parser = argparse.ArgumentParser()

    required = parser.add_argument_group("required arguments")


    if endstation:
        parser.add_argument("-e", "--endstation", choices=endstations, default=endstation, help=f"endstation name (default: {endstation})")
    else:
        required.add_argument("-e", "--endstation", required=True, choices=endstations, help=f"endstation name")

    required.add_argument("-p", "--pgroup", required=True, type=validate_pgroup, help="pattern: p12345")
    required.add_argument("-r", "--run", required=True, type=int, help="integer run number")
    parser.add_argument("-a", "--acq", nargs="*", type=int, help="integer acquisition number(s) (default: all acquisition numbers of the selected run)")

    parser.add_argument("-b", "--broker", default=API_ADDR, help=f"broker REST-API address (default: {API_ADDR})")

    parser.add_argument("-c", "--continue", dest="continue_run", action="store_true", help="append to existing run (default: create new run)")
    parser.add_argument("-d", "--dry-run", action="store_true", help="enable dry run")
#    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose mode")

    clargs = parser.parse_args()

    restapi.dry_run = clargs.dry_run

    post_retrieve(
        clargs.broker,
        clargs.endstation,
        clargs.pgroup,
        clargs.run,
        acqs=clargs.acq,
        continue_run=clargs.continue_run
    )





if __name__ == "__main__":
    main()



