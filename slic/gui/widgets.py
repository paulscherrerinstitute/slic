import wx
import wx.lib.mixins.listctrl as listmix

from fuzzywuzzy import process #TODO make this only optional?

from slic.utils import arithmetic_eval, typename

from .fname import increase, decrease
from .helper import exception_to_warning



class PersistableWidget:
    pass



WX_DEFAULT_RESIZABLE_DIALOG_STYLE = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX


class EXPANDING: pass
class STRETCH: pass


ADJUSTMENTS = {
    wx.WXK_UP: increase,
    wx.WXK_DOWN: decrease
}


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
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        hld = HeaderedListDisplay(self, sequence)
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hld, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)



class DoubleListDialog(ListDialog):

    def __init__(self, title, sequence1, sequence2, header1="entries", header2="entries"):
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

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
        if sequence:
            self.InsertItems(sequence, 0)

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_copy)


    def on_copy(self, event):
        val = self.GetStringSelection()
        print(val)
        copy_to_clipboard(val)



class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, parent, columns, *args, **kwargs):
        wx.ListCtrl.__init__(self, parent, *args, **kwargs)

        for c in columns:
            self.AppendColumn(c, width=wx.LIST_AUTOSIZE_USEHEADER)

        listmix.ListCtrlAutoWidthMixin.__init__(self)


    def Append(self, *args, color=None, **kwargs):
        index = wx.ListCtrl.Append(self, *args, **kwargs)
        self.apply_color(index, color)
        self.autosize()
        return index

    def Prepend(self, *args, **kwargs):
        return self.Insert(0, *args, **kwargs)

    def Insert(self, index, entry, color=None):
        self.InsertItem(index, "")
        for i, v in enumerate(entry):
            self.SetItem(index, i, str(v))
        self.apply_color(index, color)
        self.autosize()
        return index

    def apply_color(self, index, color):
        if color is not None:
            self.SetItemBackgroundColour(index, color)

    def autosize(self):
        ncol = self.GetColumnCount()
        ncol -= 1 # do not set last col as it is handled by ListCtrlAutoWidthMixin
        for i in range(ncol):
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)


    def GetItemsText(self, col=None):
        res = []
        nitems = self.GetItemCount()
        for i in range(nitems):
            if col is not None:
                line = self.GetItemText(i, col)
            else:
                line = []
                ncol = self.GetColumnCount()
                for c in range(ncol):
                    x = self.GetItemText(i, c)
                    line.append(x)
            res.append(line)
        return res



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
            try:
                return handler(*args, **kwargs)
            except Exception as e:
                exception_to_warning(e, stacklevel=2)
                post_event(wx.EVT_BUTTON, self.btn2)
        self.btn1.Bind(event, wrapped, *args, **kwargs)

    def Bind2(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable2()
            try:
                return handler(*args, **kwargs)
            except Exception as e:
                exception_to_warning(e, stacklevel=2)
#                post_event(wx.EVT_BUTTON, self.btn1) # better not press start again if stop crashed
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
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = MathEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

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
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class LabeledMathEntry(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = MathEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class MathEntry(wx.TextCtrl, PersistableWidget):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_PROCESS_ENTER
        else:
            kwargs["style"] = wx.TE_PROCESS_ENTER

        wx.TextCtrl.__init__(self, *args, **kwargs)

        self._alarm = False
        self._last_good_value = self.GetValue()

        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KEY_UP, self.on_escape)


    def SetValue(self, val):
        val = str(val)
        super().SetValue(val)


    def on_enter(self, event):
        val = self.GetValue()

        self._unset_alarm()

        try:
            val = arithmetic_eval(val)
        except SyntaxError as e:
            en = typename(e)
            msg = e.args[0]
            msg = f"{en}: {msg}"
            self._set_alarm(msg)
            self.SetInsertionPoint(e.offset)
        except Exception as e:
            en = typename(e)
            msg = f"{en}: {e}"
            self._set_alarm(msg)
            self.SetInsertionPointEnd()
        else:
            self.SetValue(val)
            self._last_good_value = val

        event.Skip()


    def on_escape(self, event):
        code = event.GetKeyCode()
        if code != wx.WXK_ESCAPE:
            event.Skip()
            return

        if self._alarm:
            self.SetValue(self._last_good_value)
            self._unset_alarm()


    def _set_alarm(self, msg):
        self._alarm = True
        self.SetToolTip(msg)
        self.SetForegroundColour(wx.RED)

    def _unset_alarm(self):
        self._alarm = False
        self.SetToolTip(None)
        self.SetForegroundColour(wx.NullColour)



class LabeledFilenameEntry(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = FilenameEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class FilenameEntry(wx.TextCtrl, PersistableWidget):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_RIGHT
        else:
            kwargs["style"] = wx.TE_RIGHT

        super().__init__(*args, **kwargs)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)


    def on_key_press(self, event):
        key = event.GetKeyCode()
        if key in ADJUSTMENTS:
            adjust = ADJUSTMENTS[key]
            self._update_value(adjust)
        else:
            event.Skip()

    def _update_value(self, adjust):
        val = self.GetValue()
        val = adjust(val)
        self.SetValue(val)
        self.SetInsertionPointEnd()

    def GetValue(self):
        return super().GetValue().strip()



class MainPanel(wx.Panel): #TODO: This still needs work

    def wrap(self, inner):
        self.sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(inner, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)



class NotebookDX(wx.Notebook):

    def SetSelection(self, num):
        ntotal = super().GetPageCount()
        num %= ntotal # allow counting from the back using negative numbers
        super().SetSelection(num)

    def AddPage(self, panel, name=None, **kwargs):
        if name is None:
            name = panel.GetName()
        super().AddPage(panel, name, **kwargs)



class FuzzyTextCompleter(wx.TextCompleterSimple):

    def __init__(self, choices, separator, limit=20, score_threshold=0):
        super().__init__()
        self.choices = choices
        self.separator = separator
        self.limit = limit
        self.score_threshold = score_threshold

    def GetCompletions(self, prefix):
        if not prefix:
            return []
        res = process.extract(prefix, self.choices, limit=self.limit)
        res = (match for match, score in res if score > self.score_threshold)
        res = (prefix + self.separator + match for match in res)
        return tuple(res)



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

    for i in widgets:
        if i is STRETCH:
            box.AddStretchSpacer()
        elif i is EXPANDING:
            expand = True # store for (and then apply to) next widget
        else:
            prop = proportion
            if expand:
                expand = False # apply only once
                prop = OTHER_PROP[prop] # other proportion makes widget expanding
            box.Add(i, proportion=prop, flag=flag, border=border)

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



