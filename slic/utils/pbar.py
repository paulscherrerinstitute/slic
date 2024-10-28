import functools
from .progress import Progress


class ProgressBar:
    """
    ProgressBar wraps a rich.progress.Task acting as a per-bar context manager.
    Alternatively, it accepts an iterable as argument and can then be iterated over to provide a progress bar.
    Nesting of ProgressBars is automatically handled by ProgressBarManager.
    """

    def __init__(self, pbm, iterable=None, description="", **kwargs):
        self.pbm = pbm
        self.iterable = iterable
        self.description = description
        self.kwargs = kwargs
        self.task = None

    def update(self, *args, **kwargs):
        self.pbm.progress.update(self.task, *args, **kwargs)

    def __enter__(self):
        self.pbm.start_progress()
        self.task = self.pbm.start_task(self.description, **self.kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self.pbm.stop_task(self.task)
        self.pbm.stop_progress(*args, **kwargs)

    def __iter__(self):
        iterable = self.iterable
        self.kwargs.setdefault("total", len(iterable))
        with self:
            for i in iterable:
                yield i
                self.update(advance=1)


class ProgressBarManager:
    """
    ProgressBarManager creates rich.progress.Progress on demand.
    To achieve this, it holds a set of "open" (i.e., unfinished) tasks (i.e., bars) and
    exits the current Progress context or enters a new one only if there are no open tasks remaining.
    """

    def __init__(self):
        self.progress = None
        self.open_tasks = set()

    def start_progress(self):
        if not self.open_tasks:
            self.progress = Progress()
            self.progress.__enter__()

    def stop_progress(self, *args, **kwargs):
        if not self.open_tasks:
            self.progress.__exit__(*args, **kwargs)
            self.progress = None

    def start_task(self, *args, **kwargs):
        task = self.progress.add_task(*args, **kwargs)
        self.open_tasks.add(task)
        return task

    def stop_task(self, task):
        self.open_tasks.remove(task)



# for convenience, an instance of ProgressBarManager is created here and
# "pre-filled" into the ProgressBar constructor.
# This should have virtually no overhead.

pbm = ProgressBarManager()
pbar = functools.partial(ProgressBar, pbm)





if __name__ == "__main__":
    from time import sleep

    def scan(nscan, nacq, nmov):
        for _ in pbar(range(nscan), "[yellow]Scanning..."):
            acquire(nacq)
            move(nmov)

    def acquire(ntotal):
        for _ in pbar(range(ntotal), "[green]Acquiring..."):
            sleep(0.01) # simulate work

    def move(ntotal):
        for _ in pbar(range(ntotal), "[blue]Moving..."):
            sleep(0.00001) # simulate work


    def test1D():
        with pbar(description="test", total=10) as pb:
            for i in range(10):
                sleep(0.1)
                pb.update(advance=1)

    def test2D():
        with pbar(description="test1", total=10) as pb1, pbar(description="test2", total=20) as pb2:
            for i1 in range(10):
                pb2.update(completed=0)
                for i2 in range(20):
                    sleep(0.1)
                    pb2.update(advance=1)
                pb1.update(advance=1)

    def test2Dnested():
        with pbar(description="test1", total=10) as pb1:
            for i1 in range(10):
                with pbar(description="test2", total=20) as pb2:
                    for i2 in range(20):
                        sleep(0.1)
                        pb2.update(advance=1)
                pb1.update(advance=1)


    acquire(50)
    move(30000)
    print()

    scan(5, 25, 15000)
    scan(5, 25, 15000)
    print()

    test1D()
    test2D()
    test2Dnested()



