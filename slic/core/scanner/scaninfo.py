import os

from slic.utils import json_save


class ScanInfo:

    def __init__(self, filename_base, base_dir, adjustables, values, suffix="_scan_info.json"):
        self.base_dir = base_dir
        self.filename = os.path.join(base_dir, filename_base)
        self.filename += suffix

        names = [ta.name if hasattr(ta, "name") else "noName" for ta in adjustables] #TODO else None?
        ids =   [ta.Id   if hasattr(ta, "Id")   else "noId"   for ta in adjustables]
        self.parameters = {"name": names, "Id": ids}

        self.values_all = values

        self.values = []
        self.readbacks = []
        self.files = []
        self.info = []


    def update(self, *args):
        self.append(*args)
        self.write()

    def append(self, values, readbacks, files, info):
        if callable(info):
            info = info()
        self.values.append(values)
        self.readbacks.append(readbacks)
        self.files.append(files)
        self.info.append(info)

    def write(self):
        json_save(self.to_dict(), self.filename)

    def to_dict(self):
        scan_info_dict = {
            "scan_parameters": self.parameters,
            "scan_values_all": self.values_all,
            "scan_values":     self.values,
            "scan_readbacks":  self.readbacks,
            "scan_files":      self.files,
            "scan_info":       self.info
        }
        return scan_info_dict

    def __repr__(self):
        return "Scan info in {}".format(self.filename)



