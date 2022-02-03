from .jsonext import json_load


class Config:

#    elog_url = user = screenshot_directory = pgroup = None

    def __init__(self, fname):
        cfg = json_load(fname)
        self.__dict__.update(cfg)



