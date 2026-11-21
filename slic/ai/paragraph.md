This is a slic session of an endstation, set up by the endstation's startup script. slic is the Python library used to control the endstation's hardware: adjustables, devices, acquisitions and Scanners.

- The objects in the object list include the configured devices, acquisitions and Scanners.
- Where the session lacks something, import it from slic or the endstation code, and do not reinvent functionality they already provide.
- Information you are likely to miss includes PV names and scan ranges: ask for them instead of guessing.

SwissFEL has two beamlines, Aramis (hard X-rays) and Athos (soft X-rays), with three endstations each:

- Aramis: 1. Alvra,      2. Bernina, 3. Cristallina
- Athos:  1. Diavolezza, 2. Maloja,  3. Furka

PV names and IDs encode this:
`SAR` is SwissFEL Aramis, `SAT` is SwissFEL Athos, `ES` is endstation.
The first digit after `ES` enumerates the endstation. The second digit enumerates instruments within the respective endstation.
For example, `SARES11-...` belongs to instrument 1 in Alvra and `SATES24-...` to instrument 4 in Maloja.

