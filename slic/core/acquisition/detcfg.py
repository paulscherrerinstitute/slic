from collections.abc import Sequence
from numbers import Number

from slic.utils.printing import printable_dict_of_dicts, printable_dict
from slic.utils.dictext import AttrDict, DictUpdateMixin

from .broker.brokerconfig import flatten_detectors #TODO: should probably move here


ALLOWED_DETECTOR_PARAMS = dict(
    adc_to_energy = bool,
    compression = bool,
    crystfel_lists_laser = bool,
    disabled_modules = Sequence,
    double_pixels_action = ["mask", "interp", "keep"],
    downsample = tuple,
    factor = Number,
    geometry = bool,
    remove_raw_files = bool,
    roi = dict, #TODO: check on contents of the dict?
    save_dap_results = bool
)


def _make_add_docstring(params):
    formatted_types = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in params.items()}
    table = "\n".join(f"- {k} = {v}" for k, v in formatted_types.items())
    return f"kwargs can be any of:\n{table}"



class _Params(DictUpdateMixin, AttrDict):

    # this class is not meant to be used directly
    # overwrite allowed_params in a subclass

    allowed_params = {}

    def __dir__(self):
        return tuple(self.allowed_params)

    def __setitem__(self, key, value):
        self._check_consistency(key, value)
        super().__setitem__(key, value)

    def __repr__(self):
        return printable_dict(self) or "no parameters configured"

    def _check_consistency(self, k, v):
        allowed_params = self.allowed_params

        if k not in allowed_params:
            printable_allowed_params = str(tuple(allowed_params))
            raise ValueError(f"parameter {repr(k)} is not from the allowed parameters {printable_allowed_params}")

        typ = allowed_params[k]
        if isinstance(typ, list):
            if v not in typ:
                raise ValueError(f"value of parameter {repr(k)} ({v}) has to be from {typ}")

        elif not isinstance(v, typ):
            tn_right = typ.__name__
            tn_wrong = type(v).__name__
            raise TypeError(f"value of parameter {repr(k)} ({v}) has to be of type {tn_right} but is {tn_wrong}")



class _Config(DictUpdateMixin, dict):

    # this class is not meant to be used directly
    # overwrite ParamsClass in a subclass

    ParamsClass = _Params

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
            if args is None:
                args = []
        dets_args   = flatten_detectors(args)
        dets_kwargs = flatten_detectors(kwargs)
        dets = dict(**dets_args, **dets_kwargs)
        for k, v in dets.items():
            self.add(k, **v)

    def __dir__(self):
        return ["add", "remove", "names"]

    def add(self, name, **kwargs):
        self[name] = kwargs

    add.__doc__ = "there are no allowed kwargs for this base class"

    def remove(self, name):
        del self[name]

    @property
    def names(self):
        return list(self.keys())

    def __setitem__(self, key, value):
        value = self.ParamsClass(**value)
        super().__setitem__(key, value)

    def __repr__(self):
        return printable_dict_of_dicts(self) or "no detectors configured"



class DetectorParams(_Params):

    allowed_params = ALLOWED_DETECTOR_PARAMS



class DetectorConfig(_Config):

    ParamsClass = DetectorParams

    #TODO:
    # if there is no duplicate function here, the following changes the docstring of the parent class
    # how to allow a dynamic docstring without re-defining the function?
    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)

    add.__doc__ = _make_add_docstring(ParamsClass.allowed_params)



