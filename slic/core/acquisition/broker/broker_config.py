from slic.utils.printing import printable_dict

from .broker_tools import clean_output_dir


class BrokerConfig:

    def __init__(self, pgroup, rate_multiplicator=1, append_user_tag_to_data_dir=False, client_name=None, **kwargs):
        self.pgroup = pgroup
        self.rate_multiplicator = rate_multiplicator #TODO: can we read that from epics?
        self.append_user_tag_to_data_dir = append_user_tag_to_data_dir
        self.client_name = client_name
        self.kwargs_init = kwargs # unknown arguments will be forwarded verbatim to the broker
        self.set(None) #TODO: sensible defaults?


    def set(self, output_dir, detectors=None, channels=None, pvs=None, scan_info=None, **kwargs):
        # output dir needs to be cleaned if used as part of the folder name
        if self.append_user_tag_to_data_dir:
            output_dir = clean_output_dir(output_dir)

        self.output_dir = output_dir
        self.detectors = detectors
        self.channels = channels
        self.pvs = pvs
        self.scan_info = scan_info
        self.kwargs_set = kwargs # unknown arguments will be forwarded verbatim to the broker


    def to_dict(self, run_number, start_pulseid, stop_pulseid):
        config = {
            "pgroup": self.pgroup,
            "rate_multiplicator": self.rate_multiplicator,
            "append_user_tag_to_data_dir": self.append_user_tag_to_data_dir,
#            "directory_name": self.output_dir, # structure <= 2021
            "user_tag": self.output_dir,        # structure >= 2022
            "run_number": run_number,           # new in 2022
            "start_pulseid": start_pulseid,
            "stop_pulseid": stop_pulseid
        }

        if self.client_name:
            config["client_name"] = self.client_name

        detectors = self.detectors
        if detectors:
            detectors = flatten_detectors(detectors)
            config["detectors"] = detectors

        if self.channels:
            bsread_channels, camera_channels = split_channels(self.channels)
            if bsread_channels:
                config["channels_list"] = bsread_channels
            if camera_channels:
                config["camera_list"] = camera_channels

        if self.pvs:
            config["pv_list"] = self.pvs

        if self.scan_info:
            config["scan_info"] = self.scan_info

        kwargs = {**self.kwargs_init, **self.kwargs_set}
        if kwargs:
            header="the following unknown arguments are forwarded verbatim to the server"
            print(printable_dict(kwargs, header=header))
            config.update(kwargs)

        return config



def split_channels(channels):
    bsread_channels = []
    camera_channels = []
    for c in channels:
        if c.endswith(":FPICTURE"):
            camera_channels.append(c)
        else:
            bsread_channels.append(c)

    return bsread_channels, camera_channels



def flatten_detectors(dets):
    if isinstance(dets, str): #TODO: improve that logic
        dets = [dets]

    if isinstance(dets, dict):
        return harmonize_detector_dict(dets)

    if isinstance(dets, (list, tuple)):
        res = {}
        for d in dets:
            if isinstance(d, dict):
                d = harmonize_detector_dict(d)
                res.update(d)
            elif isinstance(d, str):
                res[d] = {} # defaults via empty dict
            else:
                raise ValueError(f"Cannot interpret \"{d}\" as detector")
        return res

    raise ValueError(f"Cannot interpret \"{dets}\" as detector(s)")


def harmonize_detector_dict(d):
    if "name" in d:
        name = d["name"]
        d = {
            name: {
                k: v for k, v in d.items() if k != "name"
            }
        }
    return d



