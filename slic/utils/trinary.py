
ALLOWED_VALUES = (True, False, None)

def check_trinary(val, allowed_values=ALLOWED_VALUES):
    if val not in allowed_values:
        raise ValueError(f"Trinary {val!r} not in {allowed_values}")


