from pathlib import Path


class RunFilenameGenerator:

    def __init__(self, path, prefix="run", Ndigits=4, separator="_", suffix="json"):
        self.separator = separator
        self.prefix = prefix
        self.Ndigits = Ndigits
        self.path = Path(path)
        self.suffix = suffix

    def get_existing_runnumbers(self):
        pattern = self.prefix + self.Ndigits * "[0-9]" + self.separator + "*." + self.suffix
        fl = self.path.glob(pattern)
        fl = [tf for tf in fl if tf.is_file()]
        runnos = [int(tf.name.split(self.prefix)[1].split(self.separator)[0]) for tf in fl]
        return runnos

    def get_nextrun_filename(self, name):
        runnos = self.get_existing_runnumbers()
        if runnos:
            runno = max(runnos) + 1
        else:
            runno = 0
        return self.prefix + "{{:0{:d}d}}".format(self.Ndigits).format(runno) + self.separator + name + "." + self.suffix



