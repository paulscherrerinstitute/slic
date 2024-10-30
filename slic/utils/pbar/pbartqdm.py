import re

from tqdm import tqdm


PATTERN_COLOR_AND_TEXT = re.compile(r"\[(.*?)\](.*)")


def separate_color_and_text(string):
    match = PATTERN_COLOR_AND_TEXT.match(string)
    if not match:
        return None, string
    color = match.group(1)
    text  = match.group(2)
    return color, text



class ProgressBar():
    """
    ProgressBar wraps a tqdm.tqdm mimicking the ProgressBar using rich
    rich-style strings with [color] are parsed and converted to the equivalent tqdm bar color
    """

    def __init__(self, iterable=None, description="", **kwargs):
        self.iterable = iterable
        self.description = description
        self.kwargs = kwargs
        self.task = None

    def advance(self, n=1):
        self.task.update(n=n)

    def set(self, n):
        self.task.n = n
        self.task.refresh()

    def reset(self):
        self.task.reset()

    def __enter__(self):
        self.task = task = self._mk_tqdm()
        task.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.task.__exit__(*args, **kwargs)

    def __iter__(self):
        yield from self._mk_tqdm()

    def _mk_tqdm(self):
        colour, desc = separate_color_and_text(self.description)
        return tqdm(self.iterable, desc=desc, colour=colour, **self.kwargs)



pbar = ProgressBar



