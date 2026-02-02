from logging import DEBUG
from logzero import logger as log


TRACE = DEBUG - 1 #TODO: cannot import TRACE yet


class Traceable:
    """
    Mixin that logs creation of objects via log.trace()
    """

    def __new__(cls, *args, **kwargs):
        if log.isEnabledFor(TRACE):
            cls_name = cls.__name__

            printable_args = [short_repr(i) for i in args]
            printable_kwargs = [f"{k}={short_repr(v)}" for k, v in kwargs.items()]

            combined = printable_args + printable_kwargs
            combined = ", ".join(combined)

            line = f"{cls_name}({combined})"
            log.trace(f"creating: {line}", stacklevel=2) # increase stacklevel by 1 to skip Registry

        return super().__new__(cls)



def short_repr(string, cutoff=50):
    res = repr(string)
    if len(res) > cutoff:
        res = res[:cutoff] + "..."
    return res



