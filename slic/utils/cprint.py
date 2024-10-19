from colorama import Fore, Style


_COLOR_NAMES = (
    "black",
    "blue",
    "cyan",
    "green",
    "magenta",
    "red",
    "white",
    "yellow"
)


def _load_color_variants(name):
    basename = name.upper()
    lightname = f"LIGHT{basename}_EX"

    basecolor = getattr(Fore, basename)
    lightcolor = getattr(Fore, lightname)

    # this is ordered according to brightness skipping lightcolor for symmetry
    res ={
        name + "--": basecolor + Style.DIM,
        name + "-":  lightcolor + Style.DIM,
        name + "":   basecolor,
        name + "+":  basecolor + Style.BRIGHT,
#        name + "++": lightcolor,
        name + "++": lightcolor + Style.BRIGHT
    }

    return res


COLORS = {}
for name in _COLOR_NAMES:
    COLORS.update(_load_color_variants(name))

COLORS[None] = None



def cprint(*objects, color=None, sep=" ", **kwargs):
    text = flatten_strings(objects, sep)
    return _print(color, text, kwargs)

def flatten_strings(objects, sep):
    return sep.join(str(i) for i in objects)

def _print(color, text, kwargs):
    text = colored(text, color=color)
    return print(text, **kwargs)

def colored(text, color=None):
    color = get_color(color)
    if color is None:
        return text
    return color + text + Style.RESET_ALL

def get_color(color):
    try:
        return COLORS[color]
    except KeyError as exc:
        color = repr(color)
        allowed = tuple(COLORS.keys())
        raise ValueError(f"{color} not from {allowed}") from exc



# the following creates functions from the COLORS dict which wrap their argument string in a color/reset pair

def _mk_color_func(color):
    def func(text):
        return color + text + Style.RESET_ALL
    return func

for name, color in COLORS.items():
    if name is None:
        continue
    locals()[name] = _mk_color_func(color)



