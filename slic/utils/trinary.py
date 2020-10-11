
allowed_values = (True, False, None)

def check_trinary(val):
    if val not in allowed_values:
        raise ValueError("Trinary {} not in {}".format(repr(val), allowed_values))


