import os
import sys
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
        if sys.version_info >= (3,8): #TODO: how to do this for <=3.7
            stacklevel = kwargs.get("stacklevel", 1)
#            stacklevel += 3 # Traceable with stacklevel=1: 0 logcfg => 1 debug => 2 registry => 3 actual location
            stacklevel += 2 # import logging: 0 logcfg (log_func_for_class) => 1 logcfg (import_with_log) => 2 actual location
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


def setup_import_logging():
    import builtins

    orig_import = builtins.__import__

    imports_cache = set()

    def import_with_log(*args, **kwargs):
        module = orig_import(*args, **kwargs)

        name = module.__name__
        if name not in imports_cache:
            imports_cache.add(name)
            log.trace(f"importing: {name}")

        return module

    builtins.__import__ = import_with_log



add_log_Level(log, "TRACE", logging.DEBUG-1, color="magenta")
setup_import_logging()



