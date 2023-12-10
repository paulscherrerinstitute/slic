import os
import logging
import logzero
from logzero import logger as log


def logcfg(default_loglevel="WARNING"):
    loglevel = os.environ.get("LOGLEVEL", default_loglevel).upper()
    cfg_logzero(loglevel)
    cfg_logging(loglevel)

def cfg_logzero(level):
    logzero.loglevel(level)

def cfg_logging(level):
    logger = logging.getLogger()
    logger.setLevel(level)


def add_log_Level(logger, level_name, level_value, func_name=None, color=None):
    level_name = level_name.upper()
    func_name = func_name or level_name.lower()

    logging.addLevelName(level_value, level_name)

    def log_func_for_class(self, *args, **kwargs):
        stacklevel = kwargs.get("stacklevel", 1)
        stacklevel += 3 # 4 logcfg => 3 debug => 2 registry => 1 actual location
        kwargs["stacklevel"] = stacklevel
        self.log(level_value, *args, **kwargs)

    def log_func_for_module(*args, **kwargs):
        logging.log(level_value, *args, **kwargs)

    logger_class = type(logger)

    setattr(logger_class, func_name, log_func_for_class)
    setattr(logging, func_name, log_func_for_module)
    setattr(logging, level_name, level_value)

    if color is not None:
        color = color.upper()
        color = getattr(logzero.ForegroundColors, color)
        logzero.DEFAULT_COLORS[level_value] = color



add_log_Level(log, "TRACE", logging.DEBUG-1, color="magenta")



