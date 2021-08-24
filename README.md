# SwissFEL Library for Instrument Control

_slic_ is a python library providing a toolbox for creating control environments as well as writing automation scripts or control GUIs for experiments.

_slic_ is a re-write/re-factor of [_eco_](https://github.com/paulscherrerinstitute/eco) with the aim to increase maintainability and allow easier scaling to many beamlines. The main goal was a clear separation between, on the one hand, the DAQ/scanning library and the library of general-purpose devices and, on the other hand, the beamline codes. This allows the different parts to move at different paces as well as giving a clear border between working and in-development code: New ideas and features can be build for an individual beamline, only when they are ready to be used they are generalized and moved into the library shared among the beamlines.

_slic_ consists of a [core](#sliccore) library for static recording and scans as well as a [devices](#slicdevices) library containing classes that represent physical devices. As work-in-progress, the core library has seen most changes so far while the devices have not been worked on as much. Furthermore, there's a [GUI](#slicgui) frontend built on top of _slic_ as backend included.

The beamline codes can be found here:

- [Alvra](https://gitlab.psi.ch/slic/alvra)
- [Bernina](https://gitlab.psi.ch/slic/bernina)
- [Maloja](https://gitlab.psi.ch/slic/maloja)
- [Furka](https://gitlab.psi.ch/slic/furka)

... with more to come.

Please click [here](READMORE.md) for some FAQs.

## slic.core

The core library contains 

- **scanner** — `Scanner` class collecting several types of scans, e.g., along different numbers of axes. Scans are performed by alternatingly changing one or more `Adjustables` and performing a static recording via one or more `Acquisition` objects. Optionally, each step can be tested by a `Condition`. Besides, a generator for run names/numbers and a class to hold meta information about a scan is included. 
- **acquisition** — Classes for static recording via several means available at SwissFEL. Specifically, the following packages are wrapped for a common interface:
  - [sf_daq](https://github.com/paulscherrerinstitute/sf_daq_broker) (via a standalone [BrokerClient](slic/core/acquisition/broker_client.py#L15))
  - [bsread](https://github.com/paulscherrerinstitute/bsread_python)
  - [DataAPI](https://github.com/paulscherrerinstitute/data_api_python)
  - [DIA (Detector integration API)](https://github.com/paulscherrerinstitute/sf_dia)
  - [epics PVs](https://github.com/pyepics/pyepics#pv-object-oriented-ca-interface)
- **adjustable** — ABC for physical/virtual devices that can be moved or otherwise adjusted. The `PVAdjustable` class handles interaction with the typical set of epics PV defining a device (set value, readback, moving status). A generic class is also provided, which turns a getter/setter pair into an adjustable.
- **condition** — Classes that collect statistics over a given time window and test whether a value was in a specified range often enough. This allows to define what conditions are considered good enough for a recording.
- **task** — Simplifying wrappers for python's [threading.Thread](https://docs.python.org/3/library/threading.html#threading.Thread), which allow return values and forward exceptions raised within a thread to the calling scope. A nicer `__repr__` makes tasks easier to use in ipython. More specific tasks are also available: the DAQTask can hold information about the files it is writing, and the Loop comes in two variants (infinite and with time out) that both call a function repeatedly.

### Overview: Interactions of these building blocks:

<img src="https://gitlab.psi.ch/slic/slic/-/wikis/uploads/a1234d21f423ee8f072b28e108f9792b/drawing.png" width="50%" />


## slic.devices

Collection of (mostly) well-defined and generalized devices used at SwissFEL.

A `Device` (cf. also in the [overview scheme](#overview)) is a collection of several `Adjustables` and/or other `Devices` optionally with added methods and functionality. Again, a nicely readable `__repr__` is provided. The main goal is to provide folder-like namespaces to organize adjustables in meaningful hardware abstractions and allow for better discoverabilty, e.g., via ipython's autocomplete. A simple interface is the `SimpleDevice`, which combines the `Device` class with [types.SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace).


## slic.gui

One of the goals of the "library-first" approach of _slic_ is to provide means for creating "disposable GUIs", meaning that a new GUI for a specific experiment can be created quickly relying on a solid library in the backend and giving free choice over the GUI toolkit used. Therefore, the experiment control and DAQ library is cleanly separated from the GUI code, and the interfaces are clearly defined.

_slic_ comes with an example GUI (written in [wxPython](https://wxpython.org/)) built on top:

<img src="https://gitlab.psi.ch/slic/slic/-/wikis/uploads/c8d3dfeb2d159b18c2a97db6793442cd/config.png" width="33%" />
<img src="https://gitlab.psi.ch/slic/slic/-/wikis/uploads/0c58450f1e18d134910e786fe1c33f65/scan.png"   width="33%" />
<img src="https://gitlab.psi.ch/slic/slic/-/wikis/uploads/75845df3a2e3e7019f048c37b3cf7684/tweak.png"  width="33%" />

In order to further the "disposable GUIs" concept, this GUI is very modular: Tabs can be enabled or disabled upon instantiation. Each tab interfaces a single feature of _slic_:

- Static → `Acquisition.acquire()`
- Scan → `Scanner.scan1D()`
- Tweak → `Adjustable.set_target_value()`

Additionally, the wx built-ins are extended by several widgets specific to experiment control (numeral input boxes are calculators, which perform simple math on enter press; filename boxes increment a counter at the end when pressing up; etc.), which can be re-used easily.


## slic.utils

Collection of utility functions and classes that are used throughout both of the above parts of the code. This ranges from interactive Yes/No prompts over channel lists and directory/file path handlers to printing and json helpers.



---

## Getting Started

### Latest release version

Note: Currently it is preferable to use the [current code from git](#current-code-from-git-repositories) instead of the latest release from conda.

#### Installation

The latest _slic_ release is available via [conda](https://docs.conda.io/en/latest/) from the PSI channel. You may **either** create a new dedicated environment

```bash
conda create --name slic -c paulscherrerinstitute slic
```

**or** install it (and its dependencies) into your current conda environment

```bash
conda install -c paulscherrerinstitute slic
```

The beamline codes are hosted in git repositories and should be cloned (here, with Alvra as example, for other beamlines replace `alvra` with the respective name):

- either via https:

```bash
git clone https://gitlab.psi.ch/slic/alvra.git
```

- or via ssh:

```bash
git clone git@gitlab.psi.ch:slic/alvra.git
```

#### Running

Activate the conda environment used during the [installation](#installation), e.g.,

```bash
conda activate slic
```

Until we have a small launcher script, the ipython environment for, e.g., Alvra can be started like this:

```bash
ipython -i alvra/alvra.py
```

This assumes that the command is executed from the folder where the beamline script was cloned into — adapt as necessary. This starts an interactive ipython shell from the beamline script. Again, Alvra is just an example, for other beamlines replace `alvra` with the respective name. 

### Current code from git repositories

#### Dependencies

All dependencies should be available via [conda](https://docs.conda.io/en/latest/).

A new conda environment containing all dependencies can be created from [`conda-env.yml`](conda-env.yml):

```bash
conda env create --name slic --file conda-env.yml
```

The dependencies are pulled from the PSI channel and conda-forge as needed.

Similarly, the dependencies may also be added to an existing environment:

```bash
conda activate the_target_env
conda env update --file conda-env.yml
```


#### Installation

The library and the beamline codes are stored in separate git repositories within a [gitlab group](https://gitlab.psi.ch/slic). This allows to easily check out only the desired parts.

For the most current code, both parts should be cloned (here, with Alvra as example, for other beamlines replace `alvra` with the respective name):

- either via https:

```bash
git clone https://gitlab.psi.ch/slic/slic.git
git clone https://gitlab.psi.ch/slic/alvra.git
```

- or via ssh:

```bash
git clone git@gitlab.psi.ch:slic/slic.git
git clone git@gitlab.psi.ch:slic/alvra.git
```

#### Running

Activate the conda environment into which the [dependencies were installed](#dependencies), e.g.,

```bash
conda activate slic
```

Until we have a small launcher script, the ipython environment for, e.g., Alvra can be started like this:

```bash
PYTHONPATH=slic:$PYTHONPATH ipython -i alvra/alvra.py
```

This assumes that both repos have been cloned into the same folder, and that the command is executed from that folder — adapt as necessary. The first part makes sure that the library can be found; the second starts an interactive ipython shell from the beamline script. Again, Alvra is just an example, for other beamlines replace `alvra` with the respective name. 



---

## Differences to eco

While many concepts and ideas are inherited from _eco_, _slic_ differs in several key aspects:

_eco_ is meant to run within ipython, in fact it starts its own ipython shell upon start-up, providing a control environment for experiments. It does so by parsing a dictionary of "eco components" and creating objects from those.

_slic_, as the "_l_" suggests, is meant to be used as a library from a script that may be running in, e.g., ipython, the regular python interpreter or jupyter. A specific beamline script running in an interactive ipython shell provides an environment identical to eco by importing and instantiating classes from _slic_.

Conventions are formalized by ABCs (Abstract Base Classes) in order to provide immediate error messages for incomplete new (sub-)classes. True to python's duck typing, the actual library does not enforce the use of the ABCs, they are merely meant as help for writing new sub-classes.

_slic_ is based on code from the two actively used _eco_ forks:

- [Alvra](https://git.psi.ch/swissfel/eco) (only visible from within the PSI network)
- [Bernina](https://github.com/paulscherrerinstitute/eco/tree/bernina-op)


