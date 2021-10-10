import os
import logzero


def logcfg(default_loglevel="WARNING"):
    loglevel = os.environ.get("LOGLEVEL", default_loglevel).upper()
    logzero.loglevel(loglevel)



