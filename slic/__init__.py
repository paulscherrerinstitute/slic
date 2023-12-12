
from . import core


from .utils.termtitle import termtitle as _termtitle
_termtitle("⊚slic")

from .utils.logcfg import logcfg as _logcfg
_logcfg()

from .utils.pvpreload import pvpreload as _pvpreload
_pvpreload()

#TODO: add rich to dependency list
try:
    from .utils.richcfg import richcfg as _richcfg
    _richcfg()
except Exception as e:
    print("setting up rich failed:", e)


from . import devices
from . import utils


