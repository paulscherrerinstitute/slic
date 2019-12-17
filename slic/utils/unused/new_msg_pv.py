#!/opt/gfa/python-3.5/latest/bin/python
from epics import PV
import datetime
import sys


class stationMessage:
    def __init__(self, station):
        self._BL = station

    def post(self, message):
        stationStr = self._BL
        msg = message
        date_formatted = datetime.datetime.strftime(
            datetime.datetime.now(), "%a %d-%b-%Y %H:%M:%S"
        )
        mscroll = PV("SF-OP:" + str(stationStr) + "-MSG:OP-MSCROLL.PROC")
        mscroll.value = 1
        msg1 = PV("SF-OP:" + str(stationStr) + "-MSG:OP-MSG1")
        msg1.value = msg.encode()
        date1 = PV("SF-OP:" + str(stationStr) + "-MSG:OP-DATE1")
        date1.value = date_formatted.encode()
        msg1.disconnect()
        date1.disconnect()
