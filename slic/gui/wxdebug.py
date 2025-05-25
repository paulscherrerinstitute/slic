import os
from random import randint

import wx


original_add = wx.Sizer.Add


def wxdebug():
    if "WXDEBUG" in os.environ:
        wx.Sizer.Add = debug_add


def debug_add(self, item, *args, **kwargs):
    try:
        item.SetBackgroundColour(random_color())
    except:
        pass
    return original_add(self, item, *args, **kwargs)


def random_color():
    return wx.Colour(
        randint(100, 255),
        randint(100, 255),
        randint(100, 255)
    )



