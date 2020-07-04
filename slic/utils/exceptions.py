from .utils import typename


class ChainedException(Exception):

    def __str__(self):
        printable = printable_exception(self)

        cause = self.__cause__
        if cause:
            printable += "\ncaused by "
            printable += printable_exception(cause)

        return printable



def printable_exception(exc):
    name = typename(exc)
    message = exc.args[0] if exc.args else ""
    return "{}: {}".format(name, message)



