from contextlib import AbstractContextManager
from .utils import typename, singleton


class ChainedException(Exception):

    def __str__(self):
        printable = self.args[0] if self.args else ""

        cause = self.__cause__
        if cause:
            printable += "\ncaused by "
            printable += printable_exception(cause)

        return printable



def printable_exception(exc):
    name = typename(exc)
    message = str(exc)
    return "{}: {}".format(name, message)



@singleton
class printed_exception(AbstractContextManager):

   def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            name = exc_type.__name__
            message = exc_val or ""
            print("{}: {}".format(name, message))
        return True # this causes the with statement to suppress the exception



