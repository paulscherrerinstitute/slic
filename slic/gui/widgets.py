import wx

from slic.utils import arithmetic_eval


STRETCH = None


def show_list(*args, **kwargs):
    dlg = ListDialog(*args, **kwargs)
    dlg.ShowModal()
    dlg.Destroy()

def show_two_lists(*args, **kwargs):
    dlg = DoubleListDialog(*args, **kwargs)
    dlg.ShowModal()
    dlg.Destroy()



class ListDialog(wx.Dialog):

    def __init__(self, title, sequence, header="entries"):
        wx.Dialog.__init__(self, None, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        hld = HeaderedListDisplay(self, sequence)
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hld, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)



class DoubleListDialog(ListDialog):

    def __init__(self, title, sequence1, sequence2, header1="entries", header2="entries"):
        wx.Dialog.__init__(self, None, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        hld1 = HeaderedListDisplay(self, sequence1, header=header1)
        hld2 = HeaderedListDisplay(self, sequence2, header=header2)
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hld1, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(hld2, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)



class HeaderedListDisplay(wx.BoxSizer):

    def __init__(self, parent, sequence, id=wx.ID_ANY, header="entries"):
        super().__init__(wx.VERTICAL)

        nentries = len(sequence)
        header = f"{nentries} {header}"

        st_header = wx.StaticText(parent, label=header)
        ld_sequence = ListDisplay(parent, sequence)

        self.Add(st_header, flag=wx.BOTTOM|wx.CENTER, border=10)
        self.Add(ld_sequence, proportion=1, flag=wx.ALL|wx.EXPAND)



class ListDisplay(wx.ListBox):

    def __init__(self, parent, sequence):
        wx.ListBox.__init__(self, parent)
        sequence = sorted(set(str(i) for i in sequence))
        self.InsertItems(sequence, 0)

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_copy)


    def on_copy(self, event):
        val = self.GetStringSelection()
        print(val)
        copy_to_clipboard(val)



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


    def Disable(self):
        self.btn1.Disable()
        self.btn2.Disable()

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



class LabeledTweakEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value, style=wx.TE_RIGHT)

        self.btn_left  = btn_left  = wx.Button(parent, label="<")
        self.btn_right = btn_right = wx.Button(parent, label=">")

        self.btn_ff_left  = btn_ff_left  = wx.Button(parent, label="<<")
        self.btn_ff_right = btn_ff_right = wx.Button(parent, label=">>")

        widgets = (btn_ff_left, btn_left, btn_right, btn_ff_right)
        hb_tweak = make_filled_hbox(widgets)

        self.Add(label,    flag=wx.EXPAND)
        self.Add(text,     flag=wx.EXPAND)
        self.Add(hb_tweak, flag=wx.EXPAND|wx.TOP, border=10)


    def Disable(self):
        self.text.Disable()
        self.btn_left.Disable()
        self.btn_right.Disable()
        self.btn_ff_left.Disable()
        self.btn_ff_right.Disable()


    def __getattr__(self, name):
        return getattr(self.text, name)



class LabeledEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class MathEntry(wx.TextCtrl):

    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, style=wx.TE_PROCESS_ENTER, **kwargs)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)

    def SetValue(self, val):
        val = str(val)
        super().SetValue(val)


    def on_enter(self, event):
        val = self.GetValue()

        self._unset_alarm()

        try:
            val = arithmetic_eval(val)
        except SyntaxError as e:
            msg = e.args[0]
            self._set_alarm(msg)
            self.SetInsertionPoint(e.offset)
        except Exception as e:
            msg = str(e)
            self._set_alarm(msg)
            self.SetInsertionPointEnd()
        else:
            self.SetValue(val)

        event.Skip()


    def _set_alarm(self, msg):
        self.SetToolTip(msg)
        self.SetForegroundColour(wx.RED)

    def _unset_alarm(self):
        self.SetToolTip(None)
        self.SetForegroundColour(wx.NullColour)



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



def make_filled_vbox(widgets, proportion=0, flag=wx.ALL|wx.EXPAND, border=0):
    return make_filled_box(wx.VERTICAL, widgets, proportion, flag, border)

def make_filled_hbox(widgets, proportion=1, flag=wx.ALL|wx.EXPAND, border=0):
    return make_filled_box(wx.HORIZONTAL, widgets, proportion, flag, border)


def make_filled_box(orient, widgets, proportion, flag, border):
    box = wx.BoxSizer(orient)

    for i in widgets:
        if i is STRETCH:
            box.AddStretchSpacer()
        else:
            box.Add(i, proportion=proportion, flag=flag, border=border)

    return box



def copy_to_clipboard(val):
    clipdata = wx.TextDataObject()
    clipdata.SetText(val)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()


def post_event(event, source):
    evt = wx.PyCommandEvent(event.typeId, source.GetId())
    wx.PostEvent(source, evt)



