import json
import numpy as np


class NumpyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, (np.complexfloating, complex)): # also cover complex builtin
            return {"real": obj.real, "imag": obj.imag}
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)



def json_save(what, filename, *args, indent=4, sort_keys=True, cls=NumpyJSONEncoder, **kwargs):
    with open(filename, "w") as f:
        json.dump(what, f, *args, indent=indent, sort_keys=sort_keys, cls=cls, **kwargs)

def json_load(filename, *args, **kwargs):
    with open(filename, "r") as f:
        return json.load(f, *args, **kwargs)



