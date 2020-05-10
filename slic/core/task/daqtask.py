from .task import Task


class DAQTask(Task):

    def __init__(self, *args, filename=None, filenames=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.filenames = homogenized_list(filename, filenames)



def homogenized_list(item, items):
    res = set(items)
    if item:
        res.add(item)
    res = sorted(res)
    return res



