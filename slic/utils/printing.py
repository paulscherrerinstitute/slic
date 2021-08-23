
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



def printable_table(data, labels=None):
    res = []

    if labels:
        data = [labels] + data

    cols = zip(*data)
    widths = [maxstrlen(c) for c in cols]

    formatted_data = _fmt_table_data(data, widths)
    res.extend(formatted_data)

    if labels:
        sep = _fmt_label_sep(widths, line="-")
        res.insert(1, sep) # insert behind labels

    return "\n".join(res)


def _fmt_table_data(data, widths):
    return (_fmt_table_line(entries, widths) for entries in data)

def _fmt_table_line(entries, widths):
    res = (str(c).rjust(w) for c, w in zip(entries, widths))
    return " ".join(res)

def _fmt_label_sep(widths, line="-"):
    res = (line * w for w in widths)
    return " ".join(res)



