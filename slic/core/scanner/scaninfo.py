import os

from slic.utils import json_save


class ScanInfo:

    def __init__(self, filename_base, base_dir, adjustables, values, suffix="_scan_info.json"):
        self.filename_base = filename_base
        self.base_dir = base_dir
        self.filename = os.path.join(base_dir, filename_base)
        self.filename += suffix

        self.names = names = [ta.name  if hasattr(ta, "name")  else "noName"  for ta in adjustables] #TODO else None?
        self.IDs   = IDs =   [ta.ID    if hasattr(ta, "ID")    else "noID"    for ta in adjustables]
        self.units = units = [ta.units if hasattr(ta, "units") else "noUnits" for ta in adjustables]
        self.parameters = {"name": names, "Id": IDs, "units": units}

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


    def to_sfdaq_dict(self):
        scan_name = self.filename_base.replace("/", "_") #TODO: better use "__" to easier see difference to actual _ in original string?

        #TODO: not every adjustable needs/has a raw/user/dial distinction (also readbacks_raw below)
        num_adjustables = len(self.IDs)
        offsets      = [0] * num_adjustables
        coefficients = [1] * num_adjustables

        #TODO: store last_* separately during append()?
        values    = self.values
        readbacks = self.readbacks
        last_values    = values[-1]    if values    else None
        last_readbacks = readbacks[-1] if readbacks else None

        scan_info_dict = {
            "scan_name":            scan_name,

            "name":                 self.names,
            "Id":                   self.IDs,
            "units":                self.units,
            "offset":               offsets,
            "conversion_factor":    coefficients,

            "scan_values":          last_values,
            "scan_readbacks":       last_readbacks,
            "scan_readbacks_raw":   last_readbacks #TODO
        }
        return scan_info_dict


    def __repr__(self):
        return "Scan info in {}".format(self.filename)



