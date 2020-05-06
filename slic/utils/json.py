import json


def json_dump(what, filename):
    with open(filename, "w") as f:
        json.dump(what, f, indent=4, sort_keys=True)



