from slic.core.device import Device, SimpleDevice
from slic.devices.general.smaract import SmarActAxis


class XTG(Device):

    def __init__(self, ID, name="XTG SmarAct motor positions", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        self.sample = SimpleDevice("Sample",
            x = SmarActAxis(ID + ":TRX3"),
            y = SmarActAxis(ID + ":TRY3")
        )

        self.grating1 = SimpleDevice("Grating 1",
            x = SmarActAxis(ID + ":TRX1"),
            y = SmarActAxis(ID + ":TRY1"),
            z = SmarActAxis(ID + ":TRZ1")
        )

        self.grating2 = SimpleDevice("Grating 2",
            x = SmarActAxis(ID + ":TRX2"),
            y = SmarActAxis(ID + ":TRY2"),
            z = SmarActAxis(ID + ":TRZ2")
        )



