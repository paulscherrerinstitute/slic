from functools import wraps
import numpy as np
from stand.client import Client
from slic.utils import typename


PLACEHOLDERS = (
    "comment",
    "sample"
)


def printed_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(func)
            print(args)
            print(kwargs)
            en = typename(e)
            print(f"{en}: {e}")
    return wrapper



class Spreadsheet:

    def __init__(self, adjs, placeholders=PLACEHOLDERS, host="127.0.0.1", port=8080):
        self.adjs = adjs
        self.placeholders = placeholders
        self.client = Client(host=host, port=port)


    @printed_errors
    def add(self, run, filename, n_pulses, scanned_adjs=None, scan_values=None, **kwargs):
        fixed = dict(run=run, filename=filename, n_pulses=n_pulses)

        scan_info = {}

        if scanned_adjs is not None:
            scanned_adjs = [a.name for a in scanned_adjs]
            scanned_adjs = ", ".join(scanned_adjs)
            scan_info.update(scanned_adjs=scanned_adjs)

        if scan_values is not None:
            vals = np.asarray(scan_values)
            v_min = tuple(vals.min(axis=0))
            v_max = tuple(vals.max(axis=0))
            if len(v_min) == 1: v_min = v_min[0]
            if len(v_max) == 1: v_max = v_max[0]
            n_steps = len(vals)
            scan_info.update(v_min=v_min, v_max=v_max, n_steps=n_steps)

        placeholders = {n: "" for n in self.placeholders}
        entries = self.get_adjs_values()

        resp = self.client.add_row(**fixed, **placeholders, **scan_info, **kwargs, **entries)
        print(resp)


    def get_adjs_values(self):
        return {name: adj.get() for name, adj in self.adjs.items()}



