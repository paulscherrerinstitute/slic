import os
import logzero


loglevel = os.environ.get("LOGLEVEL", "WARNING").upper()
logzero.loglevel(loglevel)



