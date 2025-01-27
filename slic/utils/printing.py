import string
from .utils import sorted_naturally


def printable_dict_of_dicts(d, sorter=sorted_naturally):
    lines = (printable_dict(v, header=k, sorter=sorter) for k, v in sorter(d.items()))
    return "\n".join(lines)


def printable_dict(d, header=None, sorter=sorted_naturally):
    length = maxstrlen(d) + 1
    lines = ("{}:{}{}".format(k, mk_pad(k, length), v) for k, v in d.items())

    if sorter:
        lines = sorter(lines)

    lines = list(lines)

    if header:
        header = format_header(header)
        lines = [header] + lines

    if lines:
        lines.append("")

    return "\n".join(lines)


def maxstrlen(seq):
    seq = [str(i) for i in seq]
    return maxlen(seq)

def maxlen(seq):
    if not seq: # max of empty sequence raises a ValueError
        return 0
    return max(len(i) for i in seq)

def mk_pad(x, length):
    return " " * (length - strlen(x))

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



def printable_table(data, labels=None, enumerate_lines=False, make_legend=False):
    res = []

    if make_legend:
        d = {k: v for k, v in zip(string.ascii_uppercase, labels)}
        pd = printable_dict(d)
        labels = list(d.keys())

    if enumerate_lines:
        numbers = list(range(len(data)))
        cols = _transpose(data)
        _prepend(numbers, cols)
        data = _transpose(cols)
        _prepend("#", labels)

    if labels:
        _prepend(labels, data)

    cols = _transpose(data)
    widths = [maxstrlen(c) for c in cols]

    formatted_data = _fmt_table_data(data, widths)
    res.extend(formatted_data)

    if labels:
        sep = _fmt_label_sep(widths, line="-")
        res.insert(1, sep) # insert behind labels

    if make_legend:
        _prepend(pd, res)

    return "\n".join(res)


def _prepend(new, lst):
    lst.insert(0, new)

def _transpose(lst):
    return list(zip(*lst))

def _fmt_table_data(data, widths):
    return (_fmt_table_line(entries, widths) for entries in data)

def _fmt_table_line(entries, widths):
    res = (str(c).rjust(w) for c, w in zip(entries, widths))
    return " ".join(res)

def _fmt_label_sep(widths, line="-"):
    res = (line * w for w in widths)
    return " ".join(res)



