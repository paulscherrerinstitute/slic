from datetime import datetime

from slic.utils.printing import printable_dict_of_dicts



EXPTIME = {
    "alvra":   0.000005,
    "bernina": 0.00001
}



class DIAConfig:

    def __init__(self, instrument, pgroup):
        self.instrument = instrument

        pgroup = str(pgroup)
        if not pgroup.startswith("p"):
            pgroup = "p" + pgroup

        if len(pgroup) != 6:
            msg = "invalid pgroup \"{}\" should have the form \"p12345\"".format(pgroup)
            raise ValueError(msg)

        self.pgroup = pgroup


    def to_dict(self, filename=None, channels=None, n_pulses=100, gain_file=None, pede_file=None, is_HG0=False):
        output_file_jf = output_file_bs = filename

        corrections_preview = bool(pede_file or gain_file)

        instrument = self.instrument
        pgroup = self.pgroup

        user = pgroup[1:]
        uid = int(user)

        now = datetime.now()
        now = str(now)

        exptime = EXPTIME[instrument]

        general_config = {
            "user_id": uid,
            "general/user": user,
            "general/process": __name__,
            "general/created": now,
            "general/instrument": instrument
        }

        bsread_config = {
            "output_file": output_file_bs,
            "channels": channels
        }

        writer_config = {
            "output_file": output_file_jf,
            "n_frames": n_pulses
        }

        backend_config = {
            "n_frames": n_pulses,
            "gain_corrections_filename": gain_file,
            "pede_corrections_filename": pede_file,
            "gain_corrections_dataset": "gains",
            "pede_corrections_dataset": "gains",
            "pede_mask_dataset": "pixel_mask",
            "activate_corrections_preview": corrections_preview,
            "is_HG0": is_HG0,
            "bit_depth": 16
        }

        detector_config = {
            "exptime": exptime,
            "cycles": n_pulses,
            "frames" : 1,
            "timing": "trigger",
            "dr": 16
        }

        if is_HG0:
            detector_config["setbit"] = "0x5d 0" # Switch detector to HG0 mode

        bsread_config.update(general_config)
        writer_config.update(general_config)

        config = {
            "bsread": bsread_config,
            "writer": writer_config,
            "backend": backend_config,
            "detector": detector_config
        }

        return config


    def __repr__(self):
        return printable_dict_of_dicts(self.to_dict())



