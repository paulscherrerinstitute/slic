
def increase(s, index=None):
    return adjust(s, index, +1)

def decrease(s, index=None):
    return adjust(s, index, -1)


def adjust(s, index, delta):
    if index is not None:
        return adjust_selected_number(s, index, delta)
    return adjust_last_number(s, delta)



def adjust_selected_number(s, index, delta):
    left, number, right = split_selected_number(s, index)
    try:
        number = adjust_maintaining_width(number, delta)
    except ValueError as e:
        print(e)
        return s
    return left + number + right


def split_selected_number(s, index):
    left, right = split_at(s, index)

    left, left_piece   = split_last_number(left)
    right_piece, right = split_first_number(right)

    number = left_piece + right_piece
    return left, number, right



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
    else:
        # last item was a digit
        i += 1
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



