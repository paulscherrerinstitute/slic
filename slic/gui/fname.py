
def increase(s):
    base, number = split_last_number(s)
    if not number:
        return base
    number = increase_maintaining_width(number)
    return base + number


def decrease(s):
    base, number = split_last_number(s)
    if not number:
        return base
    number = decrease_maintaining_width(number)
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
    for i, char in enumerate(seq):
        if not char.isdigit():
            break
    return i


def split_at(seq, i):
    return seq[:i], seq[i:]


def increase_maintaining_width(num):
    length = len(num)
    num = int(num) + 1
    num = str(num).zfill(length)
    return num


def decrease_maintaining_width(num):
    length = len(num)
    num = int(num) - 1
    num = str(num).zfill(length)
    return num





if __name__ == "__main__":
    v = extract_counter("t01est01")
    print(v)
    assert v == "t01est02"

    v = extract_counter("test_001")
    print(v)
    assert v == "test_002"

    v = "test"
    assert v == extract_counter(v)



