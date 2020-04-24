import json


def loadConfig(fina):
    with open(fina, 'r') as f:
        return json.load(f)

def writeConfig(fina, obj):
    with open(fina, 'w') as f:
        json.dump(obj, f)



class Config:

#    elog_url = user = screenshot_directory = pgroup = None

    def __init__(self, fname):
        cfg = loadConfig(fname)
        self.__dict__.update(cfg)



