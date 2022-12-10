import os
import logzero
import logging


def logcfg(default_loglevel="WARNING"):
    loglevel = os.environ.get("LOGLEVEL", default_loglevel).upper()
    cfg_logzero(loglevel)
    cfg_logging(loglevel)

def cfg_logzero(level):
    logzero.loglevel(level)

def cfg_logging(level):
    logger = logging.getLogger()
    logger.setLevel(level)



