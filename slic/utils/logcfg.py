import builtins
import os
import sys
import warnings

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
        stacklevel = kwargs.pop("stacklevel", 1)
        stacklevel += 2 # 0 here => 1 call to log.trace() => 2 actual location
        if sys.version_info >= (3,8): #TODO: how to do this for <=3.7
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
    orig_import = builtins.__import__

    imports_cache = set()

    def import_with_log(*args, **kwargs):
        # catch warnings in order to re-emit them with corrected stacklevel
        with warnings.catch_warnings(record=True) as caught_warnings:
            module = orig_import(*args, **kwargs)

        name = module.__name__
        if name not in imports_cache:
            imports_cache.add(name)
            log.trace(f"importing: {name}")

        for w in caught_warnings:
            warnings.warn(
                message=w.message,
                category=w.category,
                stacklevel=2,
                source=w.source
            )

        return module

    builtins.__import__ = import_with_log



add_log_Level(log, "TRACE", logging.DEBUG-1, color="magenta")
setup_import_logging()



