import itertools


#def xrange(start=0, stop=None, step=1):
#    if stop is None:
#        return itertools.count(start, step)
#    else:
#        return range(start, stop, step)


def xrange(*args, step=1):
    if len(args) == 0:
        start = 0
        stop = None
    elif len(args) == 1:
        start = 0
        stop = args[0]
    elif len(args) == 2:
        start, stop = args
    elif len(args) == 3:
        start, stop, step = args
    else:
        nargs = len(args)
        raise TypeError(f"xrange takes from 2 to 3 positional arguments but {nargs} were given")

#    print(start, stop, step)

    if stop is None:
        return itertools.count(start, step)
    else:
        return range(start, stop, step)





if __name__ == "__main__":
    from itertools import count

    def compare(a, b):
        if isinstance(a, count):
            a = repr(a)
        if isinstance(b, count):
            b = repr(b)
        if a != b:
            print(a, b)

    compare( xrange(), count(0) )
    compare( xrange(0), range(0) )
    compare( xrange(10), range(10) )
    compare( xrange(0, 10), range(10) )
    compare( xrange(0, 10, 2), range(0, 10, 2) )
    compare( xrange(10, step=2), range(0, 10, 2) )
    compare( xrange(step=2), count(0, 2) )



