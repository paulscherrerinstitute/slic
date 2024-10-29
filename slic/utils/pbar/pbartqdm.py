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
    def __init__(self, iterable=None, description="", **kwargs):
        self.iterable = iterable
        self.description = description
        self.kwargs = kwargs
        self.task = None

    def update(self, *args, **kwargs):
        if "advance" in kwargs:
            advance = kwargs.pop("advance")
            self.task.update(n=advance)
        if "completed" in kwargs:
            completed = kwargs.pop("completed")
            if completed == 0:
                self.task.reset()
            else:
                raise NotImplementedError(f"cannot set completed to {completed} in tqdm")
        if "description" in kwargs:
            description = kwargs.pop("description")
            self.task.set_description(description)
        if "total" in kwargs:
            total = kwargs.pop("total")
            self.task.total = total
        if kwargs:
            printable_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            raise NotImplementedError(f"cannot handle the following parameters in tqdm: {printable_kwargs}")

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



