import wx
from fuzzywuzzy import process #TODO make this only optional?


class ContainsTextCompleter(wx.TextCompleterSimple):

    def __init__(self, choices, separator):
        super().__init__()
        self.choices = choices
        self.separator = separator

    def GetCompletions(self, prefix):
        if not prefix:
            return []
        res = (string for string in self.choices if prefix.lower() in string.lower())
        res = (prefix + self.separator + match for match in res)
        return tuple(res)



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



