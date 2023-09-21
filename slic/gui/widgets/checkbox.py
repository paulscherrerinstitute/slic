import wx

from ..persist import PersistableWidget


class CheckBox(wx.CheckBox, PersistableWidget):

    def __init__(self, *args, **kwargs):
        # use label as name if no name given
        label = kwargs.get("label", None)
        if label:
            kwargs.setdefault("name", label)
        super().__init__(*args, **kwargs)



