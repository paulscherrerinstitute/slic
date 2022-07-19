import inspect


def forwards_to(func_inner, nfilled=0, appended_kwargs=None):
    """
    Decorator inserting an explicit signature for functions that forward their arguments to other function via *args/**kwargs

    The decorated function forwards its arguments to func_inner
    This decorator replaces *args and **kwargs in the signature of the decorated function with explicit arguments from the signature of func_inner
    nfilled positional arguments of func_inner are filled by the decorated function and thus ignored during the replacement
    """
    pos_inner, kw_inner = get_args(func_inner)
    pos_inner = pos_inner[nfilled:]

    def deco(func_outer):
        pos_outer, kw_outer = get_args(func_outer)

        pos_comb = merge_lists_unique(pos_outer, pos_inner)
        kw_comb  = merge_dicts_unique(kw_outer, kw_inner)

        if appended_kwargs:
            kw_comb = merge_dicts_unique(kw_comb, appended_kwargs)

        func_outer.__signature__ = make_signature(pos_comb, kw_comb)
        return func_outer

    return deco



def get_args(func):
    spec = inspect.getfullargspec(func) #TODO replace by inspect.signature?
    all_args = spec.args

    defaults = spec.defaults or []
    isplit = -len(defaults) or None

    pos, kw = split_at(all_args, isplit)
    kw = dict(zip(kw, defaults))

    #TODO treat these separately (also positional only)
    kwonly = spec.kwonlydefaults
    if kwonly:
        kw.update(kwonly)

    return pos, kw


def split_at(lst, index):
    return lst[:index], lst[index:]

def merge_lists_unique(a, b):
    only_in_b = [i for i in b if i not in a]
    return a + only_in_b

def merge_dicts_unique(a, b):
    only_in_b = {k:v for k, v in b.items() if k not in a}
    return dict(**a, **only_in_b)

def make_signature(pos, kw):
    params = make_params_pos(pos) + make_params_kw(kw)
    return inspect.Signature(parameters=params)

def make_params_pos(pos, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD):
    return [inspect.Parameter(n, kind) for n in pos]

def make_params_kw(kw, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD):
    return [inspect.Parameter(n, kind, default=v) for n, v in kw.items()]





if __name__ == "__main__":

    def old(xold, yold, a, b, c=10, d=11):
        print(a, b, c, d)

    @forwards_to(old, nfilled=2)
    def new(x, y, z, a, *args, d=12, **kwargs):
        print(x, y, z, a, d)
        return old(1, 2, a, *args, d=d, **kwargs)


    class Scanner:

        def make_scan(self, adjustables, positions, n_pulses, filename, detectors=None, channels=None, pvs=None, acquisitions=(), start_immediately=True, step_info=None, return_to_initial_values=None, repeat=1):
            pass

        @forwards_to(make_scan, nfilled=3)
        def scan1D(self, adjustable, start_pos, end_pos, step_size, *args, relative=False, **kwargs):
            pass



