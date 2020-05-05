
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



