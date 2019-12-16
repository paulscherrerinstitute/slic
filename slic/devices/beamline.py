from functools import partial

class BeamlineSwissfel:
    def __init__(self,components=['slits'],name=None):
        self.name = name
        for comp_type in components:
            self.__dict__[f'_{comp_type}'] = []
            self.__dict__[comp] = partial(self._print_component_status,comp_type)


    def append_component(self,comp_type,item):
        self.__dict__[comp_type].append(item)

    def _get_component_status(self,comp_type):
        s = []
        for comp in self.__dict__[comp_type]:
            s.append(comp.__repr__())
        return s

    def _print_component_status(self,comp_type,linker='\n'):
        s = self._get_component_status()
        print(linker.join(s))


            



class Slits:
    def __init__(self, slits):
        self.slits = slits

    def __repr__(self):
        o = []
        
        for s in self.slits:
            o.append(s.name)
            tr = s.__repr__()
            for line in tr.splitlines():
                o.append('  '+line)
        return '\n'.join(o)

        
