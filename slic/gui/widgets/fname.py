
def increase(s):
    return adjust_last_number(s, +1)

def decrease(s):
    return adjust_last_number(s, -1)


def adjust_last_number(s, delta):
    base, number = split_last_number(s)
    if not number:
        return base
    number = adjust_maintaining_width(number, delta)
    return base + number


def split_last_number(s):
    rs = reverse_string(s)

    number, base = split_first_number(rs)

    number = reverse_string(number)
    base   = reverse_string(base)

    return base, number


def split_first_number(s):
    i = count_digits(s)
    number, base = split_at(s, i)
    return number, base


def reverse_string(s):
    return "".join(reversed(s))


def count_digits(seq):
    i = 0
    for i, char in enumerate(seq):
        if not char.isdigit():
            break
    return i


def split_at(seq, i):
    return seq[:i], seq[i:]


def adjust_maintaining_width(num, delta):
    length = len(num)
    num = int(num) + delta
    num = max(num, 1) #TODO clamp decrease at 1? or 0? or allow negative numbers?
    num = str(num).zfill(length)
    return num





if __name__ == "__main__":
    v = increase("t01est01")
    print(v)
    assert v == "t01est02"

    v = increase("test_001")
    print(v)
    assert v == "test_002"

    v = "test"
    assert v == increase(v)



