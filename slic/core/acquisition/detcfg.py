#!/usr/bin/env python

from collections.abc import Mapping
from collections.abc import Sequence
from numbers import Number

from slic.utils.printing import printable_dict_of_dicts, printable_dict

from .broker_client import flatten_detectors #TODO: should probably move here


ALLOWED_PARAMS = dict(
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


ALLOWED_PARAMS_FORMATTED_TYPES = {k: v.__name__ if isinstance(v, type) else v for k, v in ALLOWED_PARAMS.items()}
ALLOWED_PARAMS_TABLE = "\n".join(f"- {k} = {v}" for k, v in ALLOWED_PARAMS_FORMATTED_TYPES.items())
PARAMS_ADD_DOCSTRING = f"kwargs can be any of:\n{ALLOWED_PARAMS_TABLE}"


class AttrDict(dict):
    """
    dict with attribute access for the keys
    """

    def __dir__(self):
        return self.keys() or super().__dir__()

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            self._raise_missing_attribute(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            self._raise_missing_attribute(name)

    def _raise_missing_attribute(self, name):
        tn = type(self).__name__
        raise AttributeError(f"{repr(tn)} object has no attribute {repr(name)}")


#TODO probably should make this an ABC to enforce setitem to exist
class DictUpdateMixin:
    """
    Mixin that enables dict init and update via setitem
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.update(**kwargs)

    def update(self, other=None, **kwargs):
        if other is not None:
            if isinstance(other, Mapping):
                other = other.items()
            for k, v in other:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v


class DetectorConfig(DictUpdateMixin, dict):

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

    add.__doc__ = PARAMS_ADD_DOCSTRING

    def remove(self, name):
        del self[name]

    @property
    def names(self):
        return list(self.keys())

    def __setitem__(self, key, value):
        value = DetectorParams(**value)
        super().__setitem__(key, value)

    def __repr__(self):
        return printable_dict_of_dicts(self)



class DetectorParams(DictUpdateMixin, AttrDict):

    def __dir__(self):
        return tuple(ALLOWED_PARAMS)

    def __setitem__(self, key, value):
        check_consistency(key, value)
        super().__setitem__(key, value)

    def __repr__(self):
        return printable_dict(self)



def check_consistency(k, v):
    if k not in ALLOWED_PARAMS:
        printable_allowed_params = str(tuple(ALLOWED_PARAMS))
        raise ValueError(f"parameter {repr(k)} is not from the allowed parameters {printable_allowed_params}")

    typ = ALLOWED_PARAMS[k]
    if isinstance(typ, list):
        if v not in typ:
            raise ValueError(f"value of parameter {repr(k)} ({v}) has to be from {typ}")

    elif not isinstance(v, typ):
        tn_right = typ.__name__
        tn_wrong = type(v).__name__
        raise TypeError(f"value of parameter {repr(k)} ({v}) has to be of type {tn_right} but is {tn_wrong}")



