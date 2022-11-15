from functools import wraps
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
    def add(self, run, filename, n_pulses, scanned_adjs="", **kwargs):
        fixed = dict(run=run, filename=filename, n_pulses=n_pulses)

        if scanned_adjs:
            scanned_adjs = [a.name for a in scanned_adjs]
            scanned_adjs = " ".join(scanned_adjs)

        placeholders = {n: "" for n in self.placeholders}
        entries = self.get_adjs_values()

        resp = self.client.add_row(**fixed, **placeholders, adjustables=scanned_adjs, **kwargs, **entries)
        print(resp)


    def get_adjs_values(self):
        return {name: adj.get() for name, adj in self.adjs.items()}



