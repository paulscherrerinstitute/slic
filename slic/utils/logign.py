import logging
from contextlib import contextmanager


#MISSING_TYPE = "'type' channel field not found. Parse as 64-bit floating-point number float64 (default)."
#with source(channels=channels, receive_timeout=-1) as src:
#    with ignore_log_msg("bsread.data.helpers", lvl=logging.WARNING, msg=MISSING_TYPE):
#        src.receive()


def ignore_log_msg(log, lvl=None, msg=None):
    """
    ignore log messages with matching lvl and msg
    log must be a logger or a logger name
    None for lvl or msg are interpreted as any level or any message
    """
    logger = logging.getLogger(log) if isinstance(log, str) else log
    filt = IgnoreMessagesFilter(lvl=lvl, msg=msg)
    return log_filter(logger, filt)


@contextmanager
def log_filter(logger, filt):
    logger.addFilter(filt)
    try:
        yield
    finally:
        logger.removeFilter(filt)



class IgnoreMessagesFilter(logging.Filter):

    def __init__(self, lvl=None, msg=None):
        self.lvl = lvl
        self.msg = msg


    def filter(self, record):
        lvl = self.lvl
        msg = self.msg

        is_lvl = (lvl is None or lvl == record.levelno or lvl.upper() == record.levelname)
        is_msg = (msg is None or msg == record.msg)

        return not (is_lvl and is_msg)



