from datetime import datetime
from time import sleep, time
import subprocess

from epics import caget
import h5py
import numpy as np

from slic.core.task import Task
from slic.utils.hastyepics import get_pv as PV
from slic.utils.pyepics import EnumWrapper



