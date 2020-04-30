from .task import Task


class Changer(Task):

    def __init__(self, target, changer, *args, **kwargs):
        self.target = target
        self.changer = changer
        func = lambda: changer(target)
        super().__init__(func, *args, **kwargs)



