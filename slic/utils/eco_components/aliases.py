import os
from pathlib import Path
import json
import logging
logger = logging.getLogger(__name__)


class Alias:
    def __init__(self, alias, channel=None, channeltype=None, parent=None):
        self.alias = alias
        self.channel = channel
        self.channeltype = channeltype
        self.children = []
        self.parent = parent

    def append(self, subalias):
        assert type(subalias) is Alias, "You can only append aliases to aliases!"
        assert not (
            subalias.alias in [tc.alias for tc in self.children]
        ), f"Alias {subalias.alias} exists already!"
        self.children.append(subalias)
        if subalias.parent is None:
            subalias.parent = self
        else:
            print(subalias.parent)
            logger.warning(f'parent of alias {subalias.alias} has been defined already {subalias.parent.alias}.')

    def get_all(self, joiner="."):
        aa = []
        if self.channel:
            ta = {}
            ta["alias"] = self.alias
            ta["channel"] = self.channel
            if self.channeltype:
                ta["channeltype"] = self.channeltype
            aa.append(ta)
        if self.children:
            for tc in self.children:
                taa = tc.get_all()
                for ta in taa:
                    aa.append(
                        {
                            "alias": joiner.join([self.alias, ta["alias"]]),
                            "channel": ta["channel"],
                            "channeltype": ta["channeltype"],
                        }
                    )
        return aa

    def get_full_name(self,joiner="."):
        name = [self.alias]
        parent = self.parent
        while not parent == None:
            name.append(parent.alias)
            parent = parent.__dict__.get('parent',None)
        if joiner:
            return joiner.join(reversed(name))
        else:
            return name



#    def add_children(self, *args):
#        self.children.append(find_aliases(*args))


def find_aliases(*args):
    o = []
    for obj in args:
        if isinstance(obj, Alias):
            o.append(obj)
        if hasattr(obj, "alias"):
            obj = obj.alias
    return tuple(o)


def append_object_to_object(obj_target, obj_init, *args, name=None, **kwargs):
    """append a new object to another object together with the alias. 
    The new object needs to be defined with a name keyword. Theadditional 
    args and kwargs are the expected input for the new opject."""
    obj_target.__dict__[name] = obj_init(*args, **kwargs, name=name)
    obj_target.alias.append(obj_target.__dict__[name].alias)


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
