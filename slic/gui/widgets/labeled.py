import wx


CLS_NAME_TEMPL = "Labeled{clsname}"

CLS_DOC_TEMPL = """
Wrapper class for {clsname} that adds a label
args and kwargs are forwarded to {clsname}. Possible arguments may be taken from here:

{clsdoc}
"""


def make_labeled(cls):
    """
    Factory for wrapper classes that add a label to the given cls

    Example:
        LabeledTextCtrl = make_labeled(wx.TextCtrl)
    """

    class _LabeledClass(wx.BoxSizer):

        def __init__(self, parent, *args, label="", **kwargs):
            super().__init__(wx.VERTICAL)

            kwargs.setdefault("name", label)

            self.label  = label  = wx.StaticText(parent, label=label)
            self.widget = widget = cls(parent, *args, **kwargs)

            self.Add(label,  flag=wx.EXPAND)
            self.Add(widget, flag=wx.EXPAND, proportion=1)


        def __getattr__(self, name):
            return getattr(self.widget, name)


    clsdoc  = cls.__doc__
    clsname = cls.__name__

    _LabeledClass.__doc__  = CLS_DOC_TEMPL.format(clsname=clsname, clsdoc=clsdoc)
    _LabeledClass.__name__ = CLS_NAME_TEMPL.format(clsname=clsname)

    return _LabeledClass



