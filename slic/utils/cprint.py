from colorama import Fore


COLORS = {
    "black":   Fore.BLACK,
    "blue":    Fore.BLUE,
    "cyan":    Fore.CYAN,
    "green":   Fore.GREEN,
    "magenta": Fore.MAGENTA,
    "red":     Fore.RED,
    "white":   Fore.WHITE,
    "yellow":  Fore.YELLOW,
    None: None
}


def ncprint(*objects, color=None, sep=" ", **kwargs):
    return cprint(*objects, color=None, sep=sep, **kwargs)

def cprint(*objects, color=None, sep=" ", **kwargs):
    color = get_color(color)
    text = flatten_strings(objects, sep)
    return _print(color, text, sep, kwargs)

def get_color(color):
    try:
        return COLORS[color]
    except KeyError as exc:
        color = repr(color)
        allowed = tuple(COLORS.keys())
        raise ValueError(f"{color} not from {allowed}") from exc

def flatten_strings(objects, sep):
    return sep.join(str(i) for i in objects)

def _print(color, text, sep, kwargs):
    if color is not None:
        text = color + text + Fore.RESET
    return print(text, sep=sep, **kwargs)



# the following creates functions from the COLORS dict which wrap their argument string in a color/reset pair

def _mk_color_func(color):
    def func(text):
        return color + text + Fore.RESET
    return func

for name, color in COLORS.items():
    if name is None:
        continue
    locals()[name] = _mk_color_func(color)



