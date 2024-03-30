import requests

from slic.utils import json_validate


def advance_run_number(address, pgroup, *args, **kwargs):
    params = {"pgroup": pgroup}
    response = post_request(address, "advance_run_number", params, *args, **kwargs)
    run_number = response["run_number"]
    run_number = int(run_number)
    return run_number

def get_run_number(address, pgroup, *args, **kwargs):
    params = {"pgroup": pgroup}
    response = get_request(address, "get_current_run_number", params, *args, **kwargs)
    run_number = response["run_number"]
    run_number = int(run_number)
    return run_number


def retrieve(address, *args, **kwargs):
    response = post_request(address, "retrieve_from_buffers", *args, **kwargs)
    res = dict(
        run_number       = int(response["run_number"]),
        acq_number       = int(response["acquisition_number"]),
        total_acq_number = int(response["unique_acquisition_number"]),
        filenames = response["files"]
    )
    return res


def get_config_pvs(address, *args, **kwargs):
    params = {}
    response = get_request(address, "get_pvlist", params, *args, **kwargs)
    return response.get("pv_list")

def set_config_pvs(address, pvs, *args, **kwargs):
    params = {"pv_list": pvs}
    response = post_request(address, "set_pvlist", params, *args, **kwargs)
    return response.get("pv_list")


def post_request(address, endpoint, params, timeout=10):
    requrl = make_requrl(address, endpoint)
    params = json_validate(params)
    response = requests.post(requrl, json=params, timeout=timeout).json()
    return validate_response(response)

def get_request(address, endpoint, params, timeout=10):
    requrl = make_requrl(address, endpoint)
    params = json_validate(params)
    response = requests.get(requrl, json=params, timeout=timeout).json()
    return validate_response(response)


def make_requrl(address, endpoint):
    address = address.rstrip("/")
    return f"{address}/{endpoint}"


def validate_response(resp):
    if resp.get("status") == "ok":
        return resp

    message = resp.get("message", "Unknown error")
    msg = f"An error happened on the server:\n{message}"
    raise BrokerError(msg)



class BrokerError(Exception):
    pass



