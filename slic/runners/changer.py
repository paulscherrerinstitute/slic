from .runner import Runner


class Changer(Runner):

    def __init__(self, target, changer, *args, **kwargs):
        self.target = target
        self.changer = changer
        func = lambda: changer(target)
        super().__init__(func, *args, **kwargs)



