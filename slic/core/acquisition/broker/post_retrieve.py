import json
from functools import partial
from glob import glob
from time import sleep

from slic.core.acquisition.broker import RESTAPI
from slic.utils import json_load


API_HOST = "sf-daq"
API_PORT = 10002
WAIT_BETWEEN_REQUESTS = 0.1 # seconds



def post_retrieve(restapi, endstation, pgroup, run, acqs=None, continue_run=False, transform=None, dry_run=False, verbosity=None):
    """
    post retrieve data from sf-daq
    acqs: sequence of integer acquisition numbers or None (default: all acquisition numbers of the selected run)
    continue_run: append to existing run (default: create new run)
    transform: function that accepts one request and returns the adjusted request
    """
    dir_run_meta = mk_dir_run_meta(endstation, pgroup, run)

    if acqs is None:
        fns = mk_fns_run(dir_run_meta)
    else:
        fns = mk_fns_acqs(dir_run_meta, acqs)

    post_retrieve_acq_jsons(restapi, fns, continue_run=continue_run, transform=transform, dry_run=dry_run, verbosity=verbosity)


def post_retrieve_acq_jsons(restapi, fns, continue_run=False, transform=None, dry_run=False, verbosity=None):
    """
    post retrieve data from sf-daq
    fns: sequence of acq json file names
    continue_run: append to existing run (default: create new run)
    """
    if not isinstance(restapi, DryRunner):
        restapi = DryRunner(restapi, dry_run=dry_run)

    if verbosity is not None:
        vprint.level = verbosity

    reqs = load_reqs(fns)

    first_fn = fns[0]
    first_req = reqs[first_fn]

    updates_run = mk_updates_run(restapi, first_req, continue_run)

    for fn, req in reqs.items():
        vprint(0, "🛠️  working on:", fn)
        vprint(2, "🔎 read original request:", pretty_dict(req))

        updates_acq = mk_updates_acq(req, continue_run)
        updates_acq.update(updates_run)
        if updates_acq:
            vprint(1, "🖊️  updating request:", pretty_dict(updates_acq))
            req.update(updates_acq)
            vprint(2, "🪥  new request:", pretty_dict(req))

        if transform:
            transformed_req = transform(req)
            if transformed_req != req:
                req = transformed_req
                vprint(1, "🖍️  transformed request:", pretty_dict(req))

        resp = restapi.retrieve(req)
        vprint(0, "💌 response:", pretty_dict(resp))
        vprint(1)

        sleep(WAIT_BETWEEN_REQUESTS)


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


def load_reqs(fns):
    res = {}
    for fn in fns:
        req = json_load(fn)
        res[fn] = req
    return res


def mk_updates_run(restapi, req, continue_run):
    updates = {
        "client_name": "post_retrieve"
    }

    if not continue_run:
        # replace old run number with next run number from the DAQ
        pgroup = req["pgroup"]
        run_number = restapi.advance_run_number(pgroup)
        updates["run_number"] = run_number

    return updates


def mk_updates_acq(req, continue_run):
    updates = {}

    if not continue_run:
        # append old run number to user tag
        run_number = req["run_number"]
        user_tag   = req["user_tag"]
        updates["user_tag"] = f"{user_tag}_rerun{run_number:04}"

    return updates



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
            return partial(vprint, 3, f"🚱 dry run -- skipping: {name}")
        return getattr(self.wrapped, name)



class VerbosePrinter:

    def __init__(self, level=0):
        self.level = level

    def __call__(self, level, *args, **kwargs):
        if level <= self.level:
            print(*args, **kwargs)


vprint = VerbosePrinter()





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
        required.add_argument("-e", "--endstation", required=True, choices=endstations, help="endstation name")

    required.add_argument("-p", "--pgroup", required=True, type=validate_pgroup, help="pattern: p12345")
    required.add_argument("-r", "--run", required=True, type=int, help="integer run number")
    parser.add_argument("-a", "--acq", nargs="*", type=int, help="integer acquisition number(s) (default: all acquisition numbers of the selected run)")

    parser.add_argument("--host", default=API_HOST, help=f"broker REST-API host (default: {API_HOST})")
    parser.add_argument("--port", default=API_PORT, help=f"broker REST-API port (default: {API_PORT})")

    parser.add_argument("-c", "--continue", dest="continue_run", action="store_true", help="append to existing run (default: create new run)")
    parser.add_argument("-d", "--dry-run", action="store_true", help="enable dry run")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="enable verbose mode (multiple -v options increase the verbosity up to a maximum of 3)")

    clargs = parser.parse_args()

    restapi = RESTAPI(clargs.host, clargs.port)

    post_retrieve(
        restapi,
        clargs.endstation,
        clargs.pgroup,
        clargs.run,
        acqs=clargs.acq,
        continue_run=clargs.continue_run,
        dry_run=clargs.dry_run,
        verbosity=clargs.verbose
    )





if __name__ == "__main__":
    main()



