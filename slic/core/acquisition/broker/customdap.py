import importlib.util as ilu
from pathlib import Path

import numpy as np

from slic.utils import LineProfiler, timeit_verbose, typename


def upload_custom_dap_script(restapi, fname, *args, name=None, **kwargs):
    try:
        name = name or Path(fname).stem
        code = read_file(fname)

        func = load_proc_from_file(fname)
        test_run(func)
    except Exception as e:
        en = typename(e)
        print(f"{en}: {e}")
        return

    msg = restapi.upload_custom_dap_script(name, code, *args, **kwargs)
    print(msg)


def read_file(fn):
    with open(fn) as f:
        return f.read()


def load_proc_from_file(fn):
    mod = load_module(fn)

    proc_func_name = "proc"
    mod_name = mod.__name__

    func = getattr(mod, proc_func_name, None) or getattr(mod, mod_name, None)
    if func is None:
        raise AttributeError(f'module "{mod_name}" contains neither "{proc_func_name}" nor "{mod_name}" function')

    return func


def load_module(file_path, module_name=None):
    module_name = module_name or Path(file_path).stem
    spec = ilu.spec_from_file_location(module_name, file_path)
    module = ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run(func, max_time=0.1):
    shape = (1024, 512) #TODO: does this have to be the correct JF's size?
    image = np.random.random(shape)
    mask = image < 0.5
    meta = {} #TODO: add some/all possible entries

    orig_meta = meta.copy()
    orig_image = image.copy()
    orig_mask = mask.copy()

    with LineProfiler() as lp:
        func(meta, image, mask)

    name = func.__name__

    if meta != orig_meta:
        raise RuntimeError(f'function "{name}" modifies the metadata -- this is not allowed, return the result(s) instead')

    compare(name, "image", orig_image, image)
    compare(name, "mask", orig_mask, mask)

    run = lambda: func(meta, image, mask)
    mean, _std, msg = timeit_verbose(run)
    print("Timing results:", msg)

    if mean <= max_time:
        return

    print("Profiling results:")
    lp.print(func.__code__.co_filename)
    print()

    raise RuntimeError(f'function "{name}" runs for {mean:.3g}s on average -- this is too slow, check the profiling results')


def compare(name, what, before, after):
    if not np.array_equal(after, before, equal_nan=True):
        print(f'function "{name}" modifies the {what} -- this has no effect outside the function itself')



