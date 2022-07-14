from datetime import datetime
from time import sleep
import subprocess

from epics import caget
import h5py
import numpy as np

from bsread import source, SUB
from cam_server_client import PipelineClient
from cam_server_client.utils import get_host_port_from_stream_address

from slic.core.task import Task
from slic.utils.pyepics import EnumWrapper
from slic.utils.hastyepics import get_pv as PV

from detector_integration_api import DetectorIntegrationClient



