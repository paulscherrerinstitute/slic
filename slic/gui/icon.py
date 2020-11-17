import os.path
import wx


def get_wx_icon(fname="icon.png"):
    iname = os.path.dirname(__file__)
    iname = os.path.join(iname, fname)
    return wx.Icon(iname)



