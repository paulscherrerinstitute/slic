from .config import initFromConfigList
from . import ecocnf


def ecoinit(*args, _mod=None, alias_namespaces=None, components=None, lazy=None):

    #TODO: workaround for *args being used here
    msg = "ecoinit: \"{}\" is mandatory, even though it is a keyword argument"
    if _mod is None:
        raise TypeError(msg.format("_mod"))
    if alias_namespaces is None:
        raise TypeError(msg.format("alias_namespaces"))
    if components is None:
        raise TypeError(msg.format("components"))

    if args:
        allnames = [tc['name'] for tc in components]
        comp_toinit = []
        for arg in args:
            if not arg in allnames:
                raise Exception(f'The component {arg} has no configuration defined!')
            else:
                comp_toinit.append(components[allnames.index(arg)])
    else:
        comp_toinit = components

    if lazy is None:
        lazy=ecocnf.startup_lazy

    op = {}
    for key, value in initFromConfigList(comp_toinit, components, lazy=lazy).items():
        # _namespace[key] = value
        _mod.__dict__[key] = value
        op[key]= value


        if not ecocnf.startup_lazy:
            try:
                for ta in value.alias.get_all():
                    alias_namespaces.bernina.update(
                        ta["alias"], ta["channel"], ta["channeltype"]
                    )
            except:
                pass
#        alias_namespaces.bernina.store()
    return op



