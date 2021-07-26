import wx
import wx.lib.mixins.listctrl as listmix

from .tools import WX_DEFAULT_RESIZABLE_DIALOG_STYLE, copy_to_clipboard


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

        hld = HeaderedListDisplay(self, sequence, header=header)
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hld, proportion=1, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)



class DoubleListDialog(wx.Dialog):

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


    def on_copy(self, _event):
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



