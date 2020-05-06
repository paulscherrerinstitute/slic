import json


def json_save(what, filename, *args, indent=4, sort_keys=True, **kwargs):
    with open(filename, "w") as f:
        json.dump(what, f, *args, indent=indent, sort_keys=sort_keys, **kwargs)

def json_load(filename, *args, **kwargs):
    with open(filename, "r") as f:
        return json.load(f, *args, **kwargs)



