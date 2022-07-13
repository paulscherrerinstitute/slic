from cam_server_client import PipelineClient

from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor
from slic.devices.general.delay_stage import DelayStage


def make_dev(ID, cls, chans):
    d = {name: cls(ch) for name, ch in chans.items()}
    return SimpleDevice(ID, **d)


class TimeTool(Device):

    def __init__(self, ID, pipeline_name=None, delay_stages=None, target_stages=None, **kwargs):
        super().__init__(ID, **kwargs)

        self.pipeline_name = pipeline_name
        self.pipeline_client = PipelineClient() if pipeline_name else None

        self.delay_stages = make_dev(ID + "-DS", DelayStage, delay_stages) if delay_stages else None
        self.target_stages = make_dev(ID + "-TS", Motor, target_stages) if target_stages else None


    @property
    def roi_signal(self):
        return self._get_cfg("roi_signal")

    @roi_signal.setter
    def roi_signal(self, values):
        return self._set_cfg("roi_signal", values)

    @property
    def roi_background(self):
        return self._get_cfg("roi_background")

    @roi_background.setter
    def roi_background(self, values):
        return self._set_cfg("roi_background", values)

    def _get_cfg(self, name):
        if self.pipeline_name is None:
            return None
        return self.pipeline_client.get_instance_config(self.pipeline_name)[name]

    def _set_cfg(self, name, value):
        if self.pipeline_name is None:
            return None
        return self.pipeline_client.set_instance_config(self.pipeline_name, {name: value})


    def __repr__(self):
        res = super().__repr__()
        s = [res]
        s.append(f"Data reduction ROIs:")
        s.append(f"- signal:     {self.roi_signal}")
        s.append(f"- background: {self.roi_background}")
        return "\n".join(s)



class SpectralEncoder(TimeTool):

    def __init__(self, ID,
        delay_stages={"spect_tt": "SLAAR21-LMOT-M553:MOT", "retroreflector": "SLAAR21-LMOT-M561:MOT"},
        target_stages={"target_x": "MOTOR_X1", "target_y": "MOTOR_Y1"},
        **kwargs
    ):
        target_stages = {k: ID + ":" + v for k, v in target_stages.items()}
        super().__init__(ID, delay_stages=delay_stages, target_stages=target_stages, **kwargs)



class SpatialEncoder(TimeTool):

    def __init__(self, ID,
        pipeline_name="SARES20-CAMS142-M4_psen_db1",
        delay_stages={"spatial_tt": "SLAAR21-LMOT-M522:MOTOR_1"},
        **kwargs
    ):
        super().__init__(ID, pipeline_name=pipeline_name, delay_stages=delay_stages, **kwargs)



