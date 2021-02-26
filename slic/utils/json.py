import json
import numpy as np


class NumpyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.generic): # covers all numpy scalars
            return obj.item()
        elif isinstance(obj, complex): # covers builtin complex
            return {"real": obj.real, "imag": obj.imag}
        return super().default(obj)



def json_validate(obj):
    return json.loads(json.dumps(obj, cls=NumpyJSONEncoder))


def json_save(what, filename, *args, indent=4, sort_keys=True, cls=NumpyJSONEncoder, **kwargs):
    with open(filename, "w") as f:
        json.dump(what, f, *args, indent=indent, sort_keys=sort_keys, cls=cls, **kwargs)

def json_load(filename, *args, **kwargs):
    with open(filename, "r") as f:
        return json.load(f, *args, **kwargs)



