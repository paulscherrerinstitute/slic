from slic.utils.printing import itemize

from .task import Task


class DAQTask(Task):

    def __init__(self, *args, filename=None, filenames=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.filenames = homogenized_list(filename, filenames)

    def wait(self):
        try:
            super().wait()
        finally:
            if self.result is not None:
                self.filenames = self.result #TODO: single/multiple?

    def __repr__(self):
        res = super().__repr__()
        if self.filenames:
            items = itemize(self.filenames, header="Output files")
            res = f"{res}\n\n{items}"
        return res



def homogenized_list(item, items):
    res = set(items)
    if item:
        res.add(item)
    res = sorted(res)
    return res



