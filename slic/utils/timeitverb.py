import numpy as np
import timeit


def timeit_verbose(func, min_time=0.2, target_time=2, min_repeat=3):
    """
    time the given func
    number of runs per repeat is chosen such that the total time per repeat >= min_time
    number of repeats is chosen such that the total time overall ~ target_time, but at least min_repeat
    returns the average and std dev per run, number of runs and number of repeats, as well as a human-readable message
    """
    timer = timeit.Timer(func)
    number, repeat = find_number_and_repeat(timer, min_time, target_time, min_repeat)
    times = run_timer(timer, number, repeat)
    mean, std = calc_stats(times, number)
    msg = f"{fmt_secs(mean)} ± {fmt_secs(std)} per loop (mean ± std. dev. of {repeat:,} runs, {number:,} loops each)"
    return mean, std, number, repeat, msg


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



