import json

import requests

from slic.utils import json_validate, typename


class RESTAPI:
    """
    Combined BrokerAPI (host:port) and BrokerSlowAPI (host_slow:port_slow)
    BrokerAPI takes precdence during attribute resolution
    host_slow defaults to host
    port_slow defaults to port+1
    """

    def __init__(self, host="sf-daq", port=10002, host_slow=None, port_slow=None):
        host_slow = host_slow or host
        port_slow = port_slow or port + 1
        self.broker_api = BrokerAPI(host, port)
        self.broker_slow_api = BrokerSlowAPI(host_slow, port_slow)
        self.apis = (self.broker_api, self.broker_slow_api)

    def __getattr__(self, name):
        for api in self.apis:
            try:
                return getattr(api, name)
            except AttributeError:
                pass
        tn = typename(self)
        raise AttributeError(f"{repr(tn)} object has no attribute {repr(name)}")

    def __dir__(self):
        this_dir = list(super().__dir__())
        api_dirs = (dir(api) for api in self.apis)
        return sorted(set(sum(api_dirs, start=this_dir)))

    def __repr__(self):
        return "\n".join(repr(api) for api in self.apis)



class BaseAPI:

    def __init__(self, host, port, protocol="http"):
        self.host = host
        self.port = port
        self.protocol = protocol

    def post(self, endpoint, params, timeout=10):
        requrl = self.url(endpoint)
        params = json_validate(params)
        response = requests.post(requrl, json=params, timeout=timeout).json()
        return validate_response(response)

    def get(self, endpoint, params, timeout=10):
        requrl = self.url(endpoint)
        params = json_validate(params)
        response = requests.get(requrl, json=params, timeout=timeout).json()
        return validate_response(response)

    def url(self, endpoint):
        return f"{self.address}/{endpoint}"

    @property
    def address(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    def __repr__(self):
        tn = typename(self)
        return f"{tn} @ {self.address}"



class BrokerAPI(BaseAPI):

    def advance_run_number(self, pgroup, *args, **kwargs):
        params = {"pgroup": pgroup}
        response = self.post("advance_run_number", params, *args, **kwargs)
        run_number = response["run_number"]
        run_number = int(run_number)
        return run_number

    def get_run_number(self, pgroup, *args, **kwargs):
        params = {"pgroup": pgroup}
        response = self.get("get_current_run_number", params, *args, **kwargs)
        run_number = response["run_number"]
        run_number = int(run_number)
        return run_number


    def retrieve(self, params, *args, **kwargs):
        response = self.post("retrieve_from_buffers", params, *args, **kwargs)
        res = {
            "run_number":       int(response["run_number"]),
            "acq_number":       int(response["acquisition_number"]),
            "total_acq_number": int(response["unique_acquisition_number"]),
            "filenames": response["files"]
        }
        return res


    def get_config_pvs(self, *args, **kwargs):
        params = {}
        response = self.get("get_pvlist", params, *args, **kwargs)
        return response.get("pv_list")

    def set_config_pvs(self, pvs, *args, **kwargs):
        params = {"pv_list": pvs}
        response = self.post("set_pvlist", params, *args, **kwargs)
        return response.get("pv_list")


    def power_on_detector(self, detector, *args, **kwargs):
        params = {"detector_name": detector}
        response = self.post("power_on_detector", params, *args, **kwargs)
        return response.get("message")

    def get_running_detectors(self, *args, **kwargs):
        params = {}
        response = self.get("get_running_detectors", params, *args, **kwargs)
        target_keys = (
            "missing_detectors",
            "running_detectors",
            "limping_detectors"
        )
        res = {k: response[k] for k in target_keys & response.keys()}
        if res:
            return res
        else:
            return response.get("detectors") #TODO: remove, kept for backwards compatibility

    def get_allowed_detectors(self, *args, **kwargs):
        params = {}
        response = self.get("get_allowed_detectors", params, *args, **kwargs)
        return response.get("detectors")

    def close_pgroup(self, pgroup, *args, **kwargs):
        params = {"pgroup": pgroup}
        response = self.post("close_pgroup_writing", params, *args, **kwargs)
        return response.get("message")

    def take_pedestal(self, pgroup, detectors, *args, rate_multiplicator=1, pedestalmode=False, **kwargs):
        params = {
            "pgroup": pgroup,
            "detectors": detectors,
            "rate_multiplicator": rate_multiplicator,
            "pedestalmode": pedestalmode
        }
        response = self.post("take_pedestal", params, *args, **kwargs)
        return response.get("message")



class BrokerSlowAPI(BaseAPI):

    def power_on_modules(self, detector, modules, *args, **kwargs):
        params = {
            "detector_name": detector,
            "modules": modules
        }
        response = self.post("power_on_modules", params, *args, **kwargs)
        return response.get("message")

    def power_off_modules(self, detector, modules, *args, **kwargs):
        params = {
            "detector_name": detector,
            "modules": modules
        }
        response = self.post("power_off_modules", params, *args, **kwargs)
        return response.get("message")


    def copy_user_files(self, pgroup, run_number, fnames, *args, **kwargs):
        params = {
            "pgroup": pgroup,
            "run_number": run_number,
            "files": fnames
        }
        response = self.post("copy_user_files", params, *args, **kwargs)
        return response


    def get_jfctrl_monitor(self, detector, *args, **kwargs):
        params = {"detector_name": detector}
        response = self.get("get_jfctrl_monitor", params, *args, **kwargs)
        return response.get("parameters")

    def get_detector_temperatures(self, detector, *args, **kwargs):
        params = {"detector_name": detector}
        response = self.get("get_detector_temperatures", params, *args, **kwargs)
        return response.get("temperatures")


    def get_detector_settings(self, detector, *args, **kwargs):
        params = {"detector_name": detector}
        response = self.get("get_detector_settings", params, *args, **kwargs)
        return response.get("parameters")

    def set_detector_settings(self, detector, parameters, *args, **kwargs):
        params = {
            "detector_name": detector,
            "parameters": parameters
        }
        response = self.post("set_detector_settings", params, *args, **kwargs)
        return response.get("changed_parameters")


    def get_dap_settings(self, detector, *args, **kwargs):
        params = {"detector_name": detector}
        response = self.get("get_dap_settings", params, *args, **kwargs)
        return response.get("parameters")

    def set_dap_settings(self, detector, parameters, *args, **kwargs):
        params = {
            "detector_name": detector,
            "parameters": parameters
        }
        response = self.post("set_dap_settings", params, *args, **kwargs)
        return response.get("changed_parameters")



def validate_response(resp):
    if resp.get("status") == "ok":
        return resp
    raise BrokerError(resp)



class BrokerError(Exception):

    def __init__(self, response):
        self.response = response

        printable_response = json.dumps(response, indent=4)

        message = response.get("message", "unknown error")
        exception = response.get("exception")

        if exception:
            message = f"{exception}: {message}"

        message = f"an error happened on the server:\n{message}\n\nfull response: {printable_response}"
        super().__init__(message)



