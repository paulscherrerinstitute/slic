import os.path
import wx


def get_wx_icon(fname="icon.png"):
    iname = get_icon_path(fname)
    return wx.Icon(iname)

def get_icon_path(fname="icon.png"):
    dname = os.path.dirname(__file__)
    return os.path.join(dname, fname)



