import traceback
from colorama import Fore as _color
from importlib import import_module
import copy

try:
    from lazy_object_proxy import Proxy as LazyProxy
except:
    print(
        "Could not find package lazy-object-proxy for lazy initialisation of devices!"
    )
    pass


def init_device(devDict, devId, args, kwargs, verbose=True):
    imp_p = devDict["eco_type"].split(sep=".")
    dev_alias = devDict["alias"]
    dev_alias = dev_alias[0].lower() + dev_alias[1:]
    eco_type_name = imp_p[-1]
    istr = "from .." + ".".join(imp_p[:-1]) + " import "
    istr += "%s as _%s" % (eco_type_name, eco_type_name)
    # print(istr)
    if verbose:
        print(("Configuring %s " % (dev_alias)).ljust(25), end="")
        print(("(%s)" % (devId)).ljust(25), end="")
    error = None
    try:
        exec(istr)
        tdev = eval("_%s(Id='%s',*args,**kwargs)" % (eco_type_name, devId))
        tdev.name = dev_alias
        tdev._z_und = devDict["z_und"]
        if verbose:
            print((_color.GREEN + "OK" + _color.RESET).rjust(5))
        return tdev
    except Exception as expt:
        # tb = traceback.format_exc()
        if verbose:
            print((_color.RED + "FAILED" + _color.RESET).rjust(5))
            # print(sys.exc_info())
        raise expt


def initDeviceAliasList(aliases, lazy=False, verbose=True):
    devices = {}
    problems = {}
    for device_Id in aliases.keys():
        alias = aliases[device_Id]["alias"]
        alias = alias[0].lower() + alias[1:]
        if "eco_type" in aliases[device_Id].keys() and aliases[device_Id]["eco_type"]:
            if "args" in aliases[device_Id].keys() and aliases[device_Id]["args"]:
                args = aliases[device_Id]["args"]
            else:
                args = tuple()

            if "kwargs" in aliases[device_Id].keys() and aliases[device_Id]["kwargs"]:
                kwargs = aliases[device_Id]["kwargs"]
            else:
                kwargs = dict()
            try:
                devices[alias] = {}
                devices[alias]["device_Id"] = device_Id
                if lazy:
                    devices[alias]["factory"] = lambda: init_device(
                        aliases[device_Id], device_Id, args, kwargs, verbose=verbose
                    )
                    dev = LazyProxy(devices[alias]["factory"])
                else:
                    dev = init_device(
                        aliases[device_Id], device_Id, args, kwargs, verbose=verbose
                    )
                devices[alias]["instance"] = dev
            except:
                device.pop(alias)
                problems[alias] = {}
                problems[alias]["device_Id"] = device_Id
                problems[alias]["trace"] = traceback.format_exc()
    return devices, problems
