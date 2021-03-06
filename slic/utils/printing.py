
def printable_dict_of_dicts(d):
    lines = (printable_dict(v, header=k) for k, v in d.items())
    return "\n".join(lines)


def printable_dict(d, header=None):
    length = maxlen(d) + 1
    lines = sorted("{}:{}{}".format(k, " "*(length-len(k)), v) for k, v in d.items())

    if header:
        header = format_header(header)
        lines = [header] + lines

    return "\n".join(lines) + "\n"


def maxlen(seq):
    if not seq: # max of empty sequence is a ValueError
        return 0
    return max(len(i) for i in seq)


def format_header(msg, line_char="-"):
    msg += ":"
    line = line_char * len(msg)
    msg += "\n" + line
    return msg


def itemize(iterable, bullet="-"):
    if not bullet.endswith(" "):
        bullet += " "
    lines = (bullet + str(i) for i in iterable)
    return "\n".join(lines)



