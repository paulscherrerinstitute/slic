
def printable_dict_of_dicts(d):
    lines = (printable_dict(v, header=k) for k, v in d.items())
    return "\n".join(lines)


def printable_dict(d, header=None):
    length = maxstrlen(d) + 1
    lines = sorted("{}:{}{}".format(k, " "*(length-strlen(k)), v) for k, v in d.items())

    if header:
        header = format_header(header)
        lines = [header] + lines

    return "\n".join(lines) + "\n"


def maxstrlen(seq):
    seq = [str(i) for i in seq]
    return maxlen(seq)

def maxlen(seq):
    if not seq: # max of empty sequence is a ValueError
        return 0
    return max(len(i) for i in seq)

def strlen(x):
    return len(str(x))


def format_header(msg, line="-"):
    msg += ":"
    line = line * len(msg)
    msg += "\n" + line
    return msg


def itemize(iterable, header=None, bullet="-"):
    if not bullet.endswith(" "):
        bullet += " "

    lines = [bullet + str(i) for i in iterable]

    if header:
        header = format_header(header)
        lines = [header] + lines

    return "\n".join(lines)



