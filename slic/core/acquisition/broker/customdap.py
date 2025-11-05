import importlib.util as ilu
from pathlib import Path

import numpy as np
import timeit

from slic.utils import LineProfiler


def upload_custom_dap_script(restapi, fname, *args, name=None, **kwargs):
    name = name or Path(fname).stem
    code = read_file(fname)

    func = load_proc_from_file(fname)
    test_run(func)

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


def timeit_verbose(func, min_time=0.2, target_time=2, min_repeat=3):
    timer = timeit.Timer(func)
    number, repeat = find_number_and_repeat(timer, min_time, target_time, min_repeat)
    times = run_timer(timer, number, repeat)
    mean, std = calc_stats(times, number)
    msg = f"{fmt_secs(mean)} ± {fmt_secs(std)} per loop (mean ± std. dev. of {repeat:,} runs, {number:,} loops each)"
    return mean, std, msg


def find_number_and_repeat(timer, min_time, target_time, min_repeat):
    """
    find number so that the total time per repeat >= min_time
    pick repeat so that the total time overall ~ target_time, but at least min_repeat
    """
    number = 1
    total_time = timer.timeit(number)
    while total_time < min_time:
        number *= 10
        total_time = timer.timeit(number)

    repeat = int(round(target_time / total_time))
    repeat = max(min_repeat, repeat)

    return number, repeat


def run_timer(timer, number, repeat):
    return [timer.timeit(number) for _ in range(repeat)]


def calc_stats(times, number):
    mean = np.mean(times) / number
    std = np.std(times) / number
    return mean, std


def fmt_secs(time):
    UNITS = {
        "n": 1e9,
        "µ": 1e6,
        "m": 1e3,
        "": 1
    }
    for prefix, factor in UNITS.items():
        current = time * factor
        if current < 1000 or factor == 1:
            return f"{current:.3g} {prefix}s"



