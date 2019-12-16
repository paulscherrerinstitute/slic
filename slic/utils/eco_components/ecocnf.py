#import logging
#import json
#from pathlib import Path
#from .utilities.config import Configuration

startup_lazy = False

scopes = [
    {"name": "Alvra", "facility": "SwissFEL", "module": "alvra"},
    {"name": "Bernina", "facility": "SwissFEL", "module": "bernina"},
    {"name": "SwissMX", "facility": "SwissFEL", "module": "swissmx"},
]


# settings = Configuration(Path.home() / '.ecorc', name='eco_startup_settings')
