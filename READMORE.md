# Everything you always wanted to know about slic (but were afraid to ask)

## How do I add a new device?

A device is abstracted either as `Adjustable` or `Device` (the latter being a collection of the former). To add a new device, e.g, as a scannable axis, you only need to create/define a new adjustable.

**All adjustables appear automatically in the GUI – no configuration or code change needed.**

Many specific devices are defined in `slic.devices`. The most common examples will be discussed below.

### Adding a Motor

Motors that are implemented as epics motor record can be added via the `Motor` class:

```python
from slic.devices.general.motor import Motor

mot = Motor("SPOES10-MANIP1:MOT1", name="Our favorite motor")
```

For delay stages, where changes might be better done in the time domain (i.e., in femtoseconds) instead of length (i.e., in millimeters) there is a `DelayStage` class available in `slic.devices.general.delay_stage`.

### Adding a PV

A PV or a set of PVs that are not full-fledged motor records but may have setpoint/readback values and a moving status can be added via the `PVAdjustable` class:

```python
from slic.core.adjustable import PVAdjustable

trigger_delay = PVAdjustable("SPOES10-CVME-EVR0:Pul1-Delay-SP", "SATES20-CVME-EVR0:Pul1-Delay-RB", accuracy=1, name="Trigger Delay")
laser_delay = PVAdjustable("SPOES10-LASER:SETVALUE", "SATES20-LASER:READBACK", "SPOES10-LASER:MOVING", name="Laser Delay")
```

### Adding a device "from scratch"

In case none of the already available adjustables fits the new device, a new implementation still does **not** have to be from scratch. slic provides help to ease the task.

#### ... using inheritance

This method gives the most flexibility and full control over what the new adjustable can do. To get started, simply subclass `Adjustable`:

```python
from slic.core.adjustable import Adjustable

class MyNewCoolThing(Adjustable):
    pass

cool = MyNewCoolThing()
```

This will lead to the following error message

```
TypeError: Can't instantiate abstract class MyNewCoolThing with abstract methods get_current_value, is_moving, set_target_value
```

... informing you that you need to implement three methods:

- `get_current_value()` → return the current value/position
- `set_target_value(value, hold=False)` → return a Task* that sets the target value/position
- `is_moving()` → return a boolean moving status

*cf. `slic.core.task.Task` and `Adjustable._as_task(...)`. (This part will be simplified soon :) )

Thus, you get to work and do that:

```python
from slic.core.adjustable import Adjustable

class MyNewCoolThing(Adjustable):

    pos = 0

    def get_current_value(self):
        return self.pos

    def set_target_value(self, value, hold=False):
        def change():
            self.pos = value
        return self._as_task(change, hold=hold)

    def is_moving(self):
        return False # OK OK, this is probably cheating ;)

cool = MyNewCoolThing()
```

This works, and we can use it like any other adjustable:

```python
In [12]: cool
Out[12]: MyNewCoolThing at 0

In [13]: cool.set(10)
Out[13]: Task: done

In [14]: cool
Out[14]: MyNewCoolThing at 10
```

#### ... using composition

Alternatively, a new adjustable may be defined via `GenericAdjustable` by a few functions (`set`, `get` and – optionally – `wait`):

```python
from slic.core.adjustable import GenericAdjustable

pos = 0

def move_motor_to(position):
    global pos
    pos = position

def where_is_motor():
    return pos

mot = GenericAdjustable(move_motor_to, where_is_motor)
```


## How do I change the channels?

The default channel list is specified when creating the `Acquisition` object. Sometimes it is useful to record a different list once in a while and then return to the default list. Instead of replacing/reloading the default list, the change can be made adhoc for both static recordings and scans:

```python
daq = SFAcquisition(instrument, pgroup, default_channels=channels)
scan = Scanner(default_acquisitions=[daq])

special_channel = ["SOME_SPECIAL:CHANNEL"]

daq.acquire(filename, channels=special_channel, n_pulses=1000)
# or
scan.scan1D(motor, start, stop, step, n_pulses, filename, channels=special_channel)
```

To change the default channel list currently used for static recordings and scans, you can simply assign the new list:

```python
daq.default_channels = special_channel
```

Since the `Scanner` uses the `Acquisition` object(s), this change will also be taken into account for scans.

PVs and detectors can be changed similarly to the above examples for BS channels.

## How do I turn off the current Condition?

Sometimes the device we are basing our decision whether the beam is in a "good" condition suddenly misbehaves. Everything looks fine otherwise, so you want to record data despite the supposedly "bad" condition.

Assuming we started from something like this

```python
check_intensity = PVCondition("SPOES10-GMD123:INTENSITY", vmin=5)
scan = Scanner(default_acquisitions=[daq], condition=check_intensity)
```

... you may just do the following to quickly get rid of the check:

```python
scan.condition = None
```

If the device starts to behave correctly again, the change is easily reverted (without restarting slic):

```python
scan.condition = check_intensity
```

## Why are some of my channels missing in the data files?

Both, BS channels and PVs may – for various reason – disappear from the archiver/data buffer, which then leads to them not being written to file.

You can check which channels are currently on the default lists in the *Config* tab of the GUI. There are three buttons for the three types of channels we have: BS channels, PVs and (Jungfrau) detectors. For the first two, **the online/offline status can be seen in the dialog that is opened by the respective button**. For BS channels, this status is queried from the "dispatcher". For PVs, a direct connection test is made from the console you are running slic on. Detectors currently cannot be queried for their status.

## Why does my scan not scan where I thought it would scan?

Did you accidentally enable/disable the "Relative to current position" checkbox in the GUI?

