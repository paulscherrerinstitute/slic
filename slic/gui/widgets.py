import wx


def show_list(*args, **kwargs):
    dlg = ListDialog(*args, **kwargs)
    dlg.ShowModal()
    dlg.Destroy()



class ListDialog(wx.Dialog):

    def __init__(self, title, sequence):
        wx.Dialog.__init__(self, None, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        nentries = len(sequence)
        header = f"{nentries} entries"

        st_header = wx.StaticText(self, label=header)
        ld_sequence = ListDisplay(self, sequence)
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(st_header, flag=wx.ALL|wx.CENTER, border=10)
        vbox.Add(ld_sequence, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)



class ListDisplay(wx.ListBox):

    def __init__(self, parent, sequence):
        wx.ListBox.__init__(self, parent)
        sequence = sorted(str(i) for i in sequence)
        self.InsertItems(sequence, 0)



class TwoButtons(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label1="Go!", label2="Stop!"):
        super().__init__(wx.HORIZONTAL)

        self.btn1 = btn1 = wx.Button(parent, label=label1)
        self.btn2 = btn2 = wx.Button(parent, label=label2)

        btn2.Disable()

        self.Add(btn1, proportion=1)
        self.Add(btn2, proportion=0)


    def Bind1(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable1()
            return handler(*args, **kwargs)
        self.btn1.Bind(event, wrapped, *args, **kwargs)

    def Bind2(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable2()
            return handler(*args, **kwargs)
        self.btn2.Bind(event, wrapped, *args, **kwargs)


    def Enable1(self):
        self.btn2.SetBackgroundColour(wx.NullColour)
        self.btn1.Enable()
        self.btn2.Disable()

    def Disable1(self):
        self.btn2.SetBackgroundColour(wx.Colour(164, 36, 23))
        self.btn1.Disable()
        self.btn2.Enable()

    Enable2 = Disable1
    Disable2 = Enable1



class LabeledEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)

    def GetValue(self):
        return self.text.GetValue()

    def __getattr__(self, name):
        return getattr(self.text, name)



class NotebookPanel(wx.Panel): #TODO: This needs work

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.notebook = notebook = wx.Notebook(self)
        self.sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(notebook, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

    def SetSelection(self, num):
        nb = self.notebook
        ntotal = nb.GetPageCount()
        num %= ntotal # allow counting from the back using negative numbers
        nb.SetSelection(num)

#    def __getattr__(self, name):
#        return getattr(self.notebook, name)



def make_filled_vbox(widgets, proportion=0, flag=wx.ALL|wx.EXPAND, border=0, stretch=True):
    return make_filled_box(wx.VERTICAL, widgets, proportion, flag, border, stretch)

def make_filled_hbox(widgets, proportion=1, flag=wx.ALL|wx.EXPAND, border=0, stretch=False):
    return make_filled_box(wx.HORIZONTAL, widgets, proportion, flag, border, stretch)


def make_filled_box(orient, widgets, proportion, flag, border, stretch):
    box = wx.BoxSizer(orient)

    if stretch:
        box.AddStretchSpacer()

    for i in widgets:
        box.Add(i, proportion=proportion, flag=flag, border=border)

    return box



