
def format_header(msg):
    msg += ":"
    line = "-" * len(msg)
    msg += "\n" + line
    return msg


def printable_dict(d):
    length = maxlen(d) + 1
    lines = sorted("{}:{}{}".format(k, " "*(length-len(k)), v) for k, v in d.items())
    return "\n".join(lines)


def maxlen(seq):
    return max(len(i) for i in seq)



