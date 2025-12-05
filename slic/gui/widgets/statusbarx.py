import wx


#TODO: use wx.Alignments?
#TODO: add top, bottom, centre?
ALIGNMENTS = [
    "fit",
    "left",
    "right",
    "center"
]


class StatusBarX(wx.StatusBar):
    """
    wx.StatusBar that can hold any number of regular widgets
    Add, Insert, Remove follow the logic of the wx.Sizer equivalents
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

        self.Bind(wx.EVT_SIZE, self.on_size)
        wx.CallAfter(self.on_size, None)


    def on_size(self, event):
        n_fields = len(self.items) or 1 # 0 is not allowed
        self.SetFieldsCount(n_fields)

        styles = [i.style for i in self.items]
        self.SetStatusStyles(styles)

        for index, item in enumerate(self.items):
            rect = self.GetFieldRect(index)

            widget = item.widget
            widget_width, widget_height = widget.GetSize()

            x, w = calc_layout(rect.x, rect.width,  widget_width,  item.align_horizontal)
            y, h = calc_layout(rect.y, rect.height, widget_height, item.align_vertical)

            widget.SetPosition((x, y))
            widget.SetSize((w, h))

        if event:
            event.Skip()


    def Add(self, *args, **kwargs):
        entry = StatusBarItem(*args, **kwargs)
        self.items.append(entry)
        wx.CallAfter(self.on_size, None)
        return entry

    def Insert(self, index, *args, **kwargs):
        entry = StatusBarItem(*args, **kwargs)
        self.items.insert(index, entry)
        wx.CallAfter(self.on_size, None)
        return entry

    def Remove(self, index):
        try:
            entry = self.items.pop(index)
        except IndexError:
            return False
        else:
            self.RemoveChild(entry.widget)
            entry.widget.Destroy() #TODO: actually destroy the widget?
            return True



class StatusBarItem(object):

    def __init__(self, widget, align_horizontal="center", align_vertical="center", style=wx.SB_NORMAL):
        self.widget = widget
        self.align_horizontal = align_horizontal
        self.align_vertical = align_vertical
        self.style = style



def calc_layout(rect_start, rect_size, widget_size, align, border=1):
    inner_start = rect_start + border
    inner_size  = rect_size - 2 * border

    # fallback to fit if the widget is too large
    if widget_size > inner_size:
        align = "fit"

    if align == "fit":
        size = inner_size
    else:
        size = widget_size

    if align == "fit" or align == "left":
        pad = 0
    elif align == "right":
        pad = inner_size - widget_size
    elif align == "center":
        pad = (inner_size - widget_size) / 2
    else:
        printable_alignments = ", ".join(ALIGNMENTS)
        raise ValueError(f'align "{align}" is not from allowed: {printable_alignments}')

    pos = inner_start + pad
    return pos, size



