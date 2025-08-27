from slic.utils.cprint import cprint, colored


BLOCK = "█" * 3 # factor 3 makes block approx. square

STATUS_COLORS = {
    "idle": "cyan",
    "error": "red",
    "waiting": "blue",
    "run_finished": None,
    "transmitting": "yellow",
    "running": "green",
    "stopped": "magenta"
}


def color_bar(d, sep=" ", block=BLOCK):
    return sep.join(status_block(block, i) for i in status_list(d))

def status_block(block, status):
    color = STATUS_COLORS.get(status)
    return colored(block, color)

def status_list(d):
    return values_sorted_by_keys(transpose(d))

def transpose(d):
    return {i: k for k, v in d.items() for i in v}

def values_sorted_by_keys(d):
    return [v for _, v in sorted(d.items())]





if __name__ == "__main__":
    for k, v in STATUS_COLORS.items():
        cprint(BLOCK, k, color=v)


    data = {
        'idle': [0, 2, 3],
        'stopped': [1, 4],
        'running': [5, 6]
    }
    cb = color_bar(data)
    print(cb)



