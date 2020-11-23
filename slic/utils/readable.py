
AVERAGE_WEEKS_PER_MONTH = 365.242 / 12 / 7

# each tuple gives a unit and the number of previous units which go into it
UNITS = (
    ("minute", 60),
    ("hour",   60),
    ("day",    24),
    ("week",    7),
    ("month",  AVERAGE_WEEKS_PER_MONTH),
    ("year",   12)
)



def readable_seconds(secs):
    # adapted from https://stackoverflow.com/a/18421524/655404
    unit, number = "second", float(abs(secs))
    for next_unit, ratio in UNITS:
        next_number = number / ratio
        # if the next number is small, don't go to the next unit.
        if next_number < 2:
            break
        unit, number = next_unit, next_number

    shown = int(round(number))
    unit += "" if shown == 1 else "s"
    return f"{shown} {unit}"



