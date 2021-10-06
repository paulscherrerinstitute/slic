
def singleton(cls):
    return cls()

def typename(obj):
    return type(obj).__name__


def next_int(nums):
    if nums:
        return max(nums) + 1
    else:
        return 0

def zero_pad(i, n):
    return str(i).zfill(n)


def iround(val):
    return int(round(val))



import re

def sorted_naturally(iterable, reverse=False):
    re_digits = re.compile("([0-9]+)")
    natural = lambda item: [int(c) if c.isdigit() else c.casefold() for c in re_digits.split(item)] 
    return sorted(iterable, key=natural, reverse=reverse)



