import wx


class AlarmMixin:

    def alarm(self, obj=None):
        obj = obj or self
        wx.GetTopLevelParent(obj).Raise()



