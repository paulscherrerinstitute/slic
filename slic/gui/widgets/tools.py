import wx


WX_DEFAULT_RESIZABLE_DIALOG_STYLE = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX



class AlarmMixin:

    def alarm(self, obj=None):
        obj = obj or self
        wx.GetTopLevelParent(obj).Raise()



def post_event(event, source):
    evt = wx.PyCommandEvent(event.typeId, source.GetId())
    wx.PostEvent(source, evt)


def copy_to_clipboard(val):
    clipdata = wx.TextDataObject()
    clipdata.SetText(val)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()



