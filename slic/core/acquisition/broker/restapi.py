import json

import requests

from slic.utils import json_validate


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
        return self.address



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


    def retrieve(self, *args, **kwargs):
        response = self.post("retrieve_from_buffers", *args, **kwargs)
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



def make_detector_parameters(
        delay = None,
        detector_mode = None,
        exptime = None,
        gain_mode = None
    ):
    parameters = _make_parameters(
        delay = delay,
        detector_mode = detector_mode,
        exptime = exptime,
        gain_mode = gain_mode
    )
    return parameters

def make_dap_parameters(
        aggregation_max = None,
        apply_additional_mask = None,
        apply_aggregation = None,
        apply_threshold = None,
        beam_center_x = None,
        beam_center_y = None,
        beam_energy = None,
        detector_distance = None,
        detector_rate = None,
        disabled_modules = None,
        do_peakfinder_analysis = None,
        do_radial_integration = None,
        do_spi_analysis = None,
        double_pixels = None,
        hitfinder_adc_thresh = None,
        hitfinder_min_pix_count = None,
        hitfinder_min_snr = None,
        laser_mode = None,
        npeaks_threshold_hit = None,
        radial_integration_silent_max = None,
        radial_integration_silent_min = None,
        roi_x1 = None,
        roi_x2 = None,
        roi_y1 = None,
        roi_y2 = None,
        select_only_ppicker_events = None,
        spi_limit = None,
        threshold_max = None,
        threshold_min = None,
        threshold_value = None
    ):
    parameters = _make_parameters(
        aggregation_max = aggregation_max,
        apply_additional_mask = apply_additional_mask,
        apply_aggregation = apply_aggregation,
        apply_threshold = apply_threshold,
        beam_center_x = beam_center_x,
        beam_center_y = beam_center_y,
        beam_energy = beam_energy,
        detector_distance = detector_distance,
        detector_rate = detector_rate,
        disabled_modules = disabled_modules,
        do_peakfinder_analysis = do_peakfinder_analysis,
        do_radial_integration = do_radial_integration,
        do_spi_analysis = do_spi_analysis,
        double_pixels = double_pixels,
        hitfinder_adc_thresh = hitfinder_adc_thresh,
        hitfinder_min_pix_count = hitfinder_min_pix_count,
        hitfinder_min_snr = hitfinder_min_snr,
        laser_mode = laser_mode,
        npeaks_threshold_hit = npeaks_threshold_hit,
        radial_integration_silent_max = radial_integration_silent_max,
        radial_integration_silent_min = radial_integration_silent_min,
        roi_x1 = roi_x1,
        roi_x2 = roi_x2,
        roi_y1 = roi_y1,
        roi_y2 = roi_y2,
        select_only_ppicker_events = select_only_ppicker_events,
        spi_limit = spi_limit,
        threshold_max = threshold_max,
        threshold_min = threshold_min,
        threshold_value = threshold_value
    )
    return parameters

def _make_parameters(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}



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



