import wx


WX_DEFAULT_RESIZABLE_DIALOG_STYLE = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX


class EXPANDING: pass
class MINIMIZED: pass
class STRETCH: pass



def post_event(event, source):
    evt = wx.PyCommandEvent(event.typeId, source.GetId())
    wx.PostEvent(source, evt)


def copy_to_clipboard(val):
    clipdata = wx.TextDataObject()
    clipdata.SetText(val)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()



def make_filled_vbox(widgets, proportion=0, flag=wx.ALL|wx.EXPAND, border=0, box=None):
    return make_filled_box(wx.VERTICAL, widgets, proportion, flag, border, box)

def make_filled_hbox(widgets, proportion=1, flag=wx.ALL|wx.EXPAND, border=0, box=None):
    return make_filled_box(wx.HORIZONTAL, widgets, proportion, flag, border, box)


def make_filled_box(orient, widgets, proportion, flag, border, box):
    if box is None:
        box = wx.BoxSizer(orient)

    OTHER_PROP = {
        0: 1,
        1: 0
    }

    expand = False
    minimal = False

    for i in widgets:
        if i is STRETCH:
            box.AddStretchSpacer()
        elif i is EXPANDING:
            expand = True # store for (and then apply to) next widget
        elif i is MINIMIZED:
            minimal = True # store for (and then apply to) next widget
        else:
            iprop = proportion
            iflag = flag
            if expand:
                expand = False # apply only once
                iprop = OTHER_PROP[iprop] # other proportion makes widget expanding
            if minimal:
                minimal = False # apply only once
                iflag = wx.ALL #TODO: calculate actual flag without wx.EXPAND?
            box.Add(i, proportion=iprop, flag=iflag, border=border)

    return box



