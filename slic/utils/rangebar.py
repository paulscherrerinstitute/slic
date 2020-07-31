import colorama

COLOR_GOOD  = colorama.Fore.GREEN
COLOR_BAD   = colorama.Fore.RED
COLOR_RESET = colorama.Fore.RESET

STYLE_EMPH  = colorama.Style.BRIGHT
STYLE_RESET = colorama.Style.RESET_ALL


BLOCKS = " ▏▎▍▌▋▊▉█"
NUM_BLOCKS = len(BLOCKS)
BLOCK_EMPTY = BLOCKS[0]
BLOCK_FULL = BLOCKS[-1]
BLOCK_OVERFLOW = ">"
BLOCK_UNDERFLOW = "<"
BLOCK_ERROR = "X"


class RangeBar:

    def __init__(self, start, stop, width=30, units=None, fmt="1.5g"):
        self.start = start
        self.stop = stop
        self.width = width
        self.units = units
        self.fmt = fmt


    def __enter__(self):
        self.show(self.start) # show initial bar (also if nothing changes)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print() # print newline after last bar update
        return (exc_type is None)


    def show(self, value):
        bar = self.get(value)
        print_and_return(bar)


    def get(self, value):
        start = self.start
        stop  = self.stop
        width = self.width

        part = calc_part(start, stop, value)
        bar = make_bar_str(part, width)

        value = self.format_number(value)
        start = self.format_number(start)
        stop  = self.format_number(stop)

        value = style_emph(value)

        return f"[ {start} |{bar}| {stop} ]   {value}"


    def format_number(self, num):
        fmt = self.fmt
        units = self.units
        units = f" {units}" if units else ""
        return f"{num:{fmt}}{units}"


    def __repr__(self):
        start = self.format_number(self.start)
        stop  = self.format_number(self.stop)
        width = self.width
        return f"[ {start} |{width} blocks| {stop} ]"



def make_bar_str(part, width):
    if 0 <= part <= 1:
        return make_bar_str_good(part, width)
    else:
        return make_bar_str_bad(part, width)


def make_bar_str_good(part, width):
    whole, fract = split_whole_fract(width * part)
    remain = width - whole - 1 # 1 for fract block

    bar = BLOCK_FULL * whole

    if remain >= 0: # if remain negative, add no empty fract block
        ifract = calc_index(fract, NUM_BLOCKS)
        bar += BLOCKS[ifract]
        bar += BLOCK_EMPTY * remain

    return color_good(bar)


def make_bar_str_bad(part, width):
    block = BLOCK_ERROR # just a safety measure

    if part < 0:
        block = BLOCK_UNDERFLOW
    elif part > 1:
        block = BLOCK_OVERFLOW

    bar = block * width
    return color_bad(bar)


def calc_part(start, stop, value):
    total_range = stop - start
    if total_range == 0:
        return 1
    value_range = value - start
    return value_range / total_range

def split_whole_fract(value):
    whole, fract = divmod(value, 1)
    whole = int(whole)
    return whole, fract

def calc_index(fract, n_total):
    index = fract * (n_total - 1)
    return int(round(index))

def color_good(string):
    return COLOR_GOOD + string + COLOR_RESET

def color_bad(string):
    return COLOR_BAD + string + COLOR_RESET

def style_emph(string):
    return STYLE_EMPH + string + STYLE_RESET

def print_and_return(*args, **kwargs):
    """prints then returns cursor to start of current line"""
    print(*args, end="\r", **kwargs)



#TODO
#- configurable blocks
#- configurable colors
#- monochrome?



