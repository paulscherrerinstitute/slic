import inspect

from slic.core.task import Task
from .utils import typename, singleton
from .registry import Registry, instances
from .printing import printable_dict


class Shortcut(Registry):

    def __init__(self, func, name=None):
        #TODO: maybe name should be mandatory?
        if name is None:
            name = func.__name__
            name = name.replace("_", " ").capitalize()

        self.func = func
        self.name = name


    def __repr__(self):
        tn = typename(self)
        return f"{tn} \"{self.name}\""


    def run(self, hold=False):
        print(f"Running \"{self.name}\"")
        return Task(self.func, hold=hold)

    __call__ = run


    @property
    def source(self):
        return inspect.getsource(self.func).strip()



def as_shortcut(func=None, *, name=None):
    """
    Use either as:

    @as_shortcut
    def a_new_func():
        pass

    -> Shortcut(func, name="a_new_func")

    ... or as:

    @as_shortcut(name="A New Func")
    def a_new_func():
        pass

    -> Shortcut(func, name="A New Func")

    """
    if func is not None:
        return Shortcut(func, name=name)

    def deco(func):
        return Shortcut(func, name=name)
    return deco



@singleton
class shortcuts:

    def __repr__(self):
        ms = self._get()
        return printable_dict(ms)

    def __getitem__(self, key):
        ms = self._get()
        return ms[key]

    def _get(self):
        return {m.name: m for m in instances(Shortcut)}



