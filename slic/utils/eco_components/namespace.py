import os
from pathlib import Path
import json


class Namespace:
    def __init__(self, namespace_file=None):
        path = Path(namespace_file)
        assert path.suffix == ".json", "file has no json extension"
        self._path = path
        self.name = path.stem
        self.data = None
        self._modified = False

    def read_file(self):
        with self._path.open("r") as fp:
            self.data = json.load(fp)
            self._modified = False

    @property
    def aliases(self):
        if not self.data:
            self.read_file()
        return [td["alias"] for td in self.data]

    @property
    def channels(self):
        if not self.data:
            self.read_file()
        return [td["channel"] for td in self.data]

    def update(self, alias, channel, channeltype):
        assert not alias in self.aliases, "Duplicate alias {alias} found!"
        assert not channel in self.channels, "Duplicate channel {channel} found!"
        self.data.append(
            {"alias": alias, "channel": channel, "channeltype": channeltype}
        )
        self._modified = True

    def store(self):
        if self._modified:
            with self._path.open("w") as fp:
                json.dump(self.data, fp)
                self._modified = False

    def get_info(self, alias=None, channel=None):
        assert alias or channel, "Either search alias or channel needs to be defined!"
        assert not (
            alias and channel
        ), "Only either search alias or channel can be defined"
        if alias:
            if alias in self.aliases:
                return self.data[self.aliases.index(alias)]
            else:
                return None
        if channel:
            if channel in self.channels:
                return self.data[self.channels.index(channel)]
            else:
                return None


class NamespaceCollection:
    def __init__(self, alias_path=None):
        if not alias_path:
            alias_path = os.path.abspath(__file__)
            self._namespace_path = Path(alias_path).parent / "namespaces"
        else:
            self._namespace_path = Path(alias_path)
        for nsf in self._namespace_path.glob("*.json"):
            # self.__dict__[nsf.stem] = property(lambda:Namespace(nsf))
            self.__dict__[nsf.stem] = Namespace(nsf)



