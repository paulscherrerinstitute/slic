STYLES = {
    "normal": "┌┐└┘──││",
    "thick":  "┏┓┗┛━━┃┃",
    "double": "╔╗╚╝══║║",

    "thick-top":  "┍┑┕┙━━││",
    "thick-side": "┎┒┖┚──┃┃",

    "double-top":  "╒╕╘╛══││",
    "double-side": "╓╖╙╜──║║",

    "fat":     "▛▜▙▟▀▄▌▐",
    "tight":   "▗▖▝▘▄▀▐▌",
    "rounded": "╭╮╰╯──││",
    "ascii":   "++++--||"
}


ALIGNMENTS = {
    "left":   "ljust",
    "center": "center",
    "right":  "rjust"
}



class Style:

    def __init__(self, chars):
        self.chars = chars
        try:
            self.top_left, self.top_right, self.bottom_left, self.bottom_right, self.top, self.bottom, self.left, self.right = chars
        except ValueError as e:
            raise ValueError(f"cannot unpack {chars!r} in style due to {e}") from e


    def make_box(self, lines, length):
        top    = self.make_top_line(length)
        middle = self.make_middle_lines(lines)
        bottom = self.make_bottom_line(length)
        return flatten(top, middle, bottom)

    def make_top_line(self, length):
        return self.top_left + self.top * length + self.top_right

    def make_middle_lines(self, lines):
        return [self.left + i + self.right for i in lines]

    def make_bottom_line(self, length):
        return self.bottom_left + self.bottom * length + self.bottom_right


    def __repr__(self):
        tn = type(self).__name__
        return f"{tn}({self.chars!r})"

    def __str__(self):
        return self.make_box("X", 1)



def boxed(text, align="left", style="normal", npad=0):
    lines = text.splitlines()
    length = maxlen(lines)

    lines = aligned(lines, length, align=align)

    if npad:
        # factor 3 makes boxes approx. square
        nvpad = int(round(npad/3))
        length += 2 * npad

        # this has to be in this order, otherwise vert_padded needs to insert lines of the correct length
        lines = vert_padded(lines, nvpad)
        lines = hori_padded(lines, length)

    style = Style(STYLES[style])
    return style.make_box(lines, length)


def maxlen(seq):
    return max(len(i) for i in seq)

def aligned(lines, length, align="left"):
    """
    align: left, center, right
    """
    try:
        meth = ALIGNMENTS[align]
    except KeyError as e:
        values = tuple(ALIGNMENTS.keys())
        raise ValueError(f"{align!r} is not from {values}") from e
    return [getattr(line, meth)(length) for line in lines]

def flatten(top, middle, bottom):
    return "\n".join([top] + middle + [bottom])

def vert_padded(lines, npad):
    padding = [" "] * npad
    return padding + lines + padding

def hori_padded(lines, length):
    return aligned(lines, length, align="center")





if __name__ == "__main__":
    style = Style(r"/\\/^_[]")
    print(repr(style))
    print(style)
    print()

    for k, v in STYLES.items():
        style = Style(v)
        print(f"{k}:")
        print(style)
        print()

    txt = "a\nbbb\nccccc"
    print(boxed(txt))
    print(boxed(txt, style="rounded", align="center", npad=3))
    print(boxed(txt, style="fat", align="right"))
    print(boxed(txt, style="tight", align="right"))



