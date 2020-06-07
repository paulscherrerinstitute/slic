# SwissFEL Library for Instrument Control

slic is a python library providing a toolbox for creating control environments as well as writing automation scripts or control GUIs for experiments.

slic is a re-write/re-factor of [eco](https://github.com/paulscherrerinstitute/eco) with the aim to increase maintainability and allow easier scaling to many beamlines. The main goal was a clear separation between, on the one hand, the DAQ/scanning library and the library of general-purpose devices and, on the other hand, the beamline codes. This allows the different parts to move at different paces as well as giving a clear border between working and in-development code: New ideas and features can be build for an individual beamline, only when they are ready to be used they are generalized and moved into the library shared among the beamlines.

slic consists of a _core_ library for static recording and scans as well as a _devices_ library containing classes that represent physical devices. As work-in-progress, the core library has seen most changes so far while the devices have not been worked on as much.

The beamline codes can be found here:

- [Alvra](https://gitlab.psi.ch/slic/alvra)
- [Bernina](https://gitlab.psi.ch/slic/bernina)

... with more to come.

## slic.core

The core library contains 

- **scanner** — Class collecting several types of scans, e.g., along different numbers of axes. Scans are performed by alternatingly changing one or more **adjustables** and performing a static recording via one or more **acquisition** objects. Optionally, each step can be tested by a **condition**. Besides, a generator for run names/numbers and a class to hold meta information about a scan is included. 
- **acquisition** — Classes for static recording via several means available at SwissFEL. Specifically, the following packages are wrapped for a common interface:
  - [bsread](https://github.com/paulscherrerinstitute/bsread_python)
  - [DataAPI](https://github.com/paulscherrerinstitute/data_api_python)
  - [DIA (Detector integration API)](https://github.com/paulscherrerinstitute/sf_dia)
  - [epics PVs](https://github.com/pyepics/pyepics#pv-object-oriented-ca-interface)
- **adjustable** — ABC for physical/virtual devices that can be moved or otherwise adjusted. A generic class is also provided, which turns a getter/setter pair into an adjustable.
- **condition** — Classes that collect statistics over a given time window and test whether a value was in a specified range often enough. This allows to define what conditions are considered good enough for a recording.
- **task** — Simplifying wrappers for python's [threading.Thread](https://docs.python.org/3/library/threading.html#threading.Thread), which allow return values and forward exceptions raised within a thread to the calling scope. A nicer `__repr__` makes tasks easier to use in ipython. More specific tasks are also available: the DAQTask can hold information about the files it is writing, and the Loop comes in two variants (infinite and with time out) that both call a function repeatedly.

## slic.devices

TBD

## slic.utils

Collection of utility functions and classes that are used throughout both of the above parts of the code. This ranges from interactive Yes/No prompts over channel lists and directory/file path handlers to printing and json helpers.



---

## Getting Started

### Latest release version

#### Installation

The latest slic release is available via [conda](https://docs.conda.io/en/latest/) from the PSI channel. You may **either** create a new dedicated environment

```bash
conda create -c paulscherrerinstitute -n slic slic
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

Then, the ipython environment can be started like this:

```bash
ipython -i alvra/alvra.py
```

This assumes that the command is executed from the folder where the beamline script was cloned into — adapt as necessary.

### Current code from git repositories

#### Dependencies

All dependencies should be available via [conda](https://docs.conda.io/en/latest/).

If need be, create a new conda environment:

```bash
conda create -n slic
conda activate slic
```

Some dependencies might need the PSI channel, thus:

```bash
conda install -c paulscherrerinstitute bsread cam_server colorama data_api detector_integration_api elog ipython jungfrau_utils pyepics
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

While many concepts and ideas are inherited from eco, slic differs in several key aspects:

eco is meant to run within ipython, in fact it starts its own ipython shell upon start-up, providing a control environment for experiments. It does so by parsing a dictionary of "eco components" and creating objects from those.

slic, as the "l" suggests, is meant to be used as a library from a script that may be running in, e.g., ipython, the regular python interpreter or jupyter. A specific beamline script running in an interactive ipython shell provides an environment identical to eco by importing and instantiating classes from slic.

Conventions are formalized by ABCs (Abstract Base Classes) in order to provide immediate error messages for incomplete new (sub-)classes. True to python's duck typing, the actual library does not enforce the use of the ABCs, they are merely meant as help for writing new sub-classes.

slic is based on code from the two actively used eco forks:

- [Alvra](https://git.psi.ch/swissfel/eco) (only visible from within the PSI network)
- [Bernina](https://github.com/paulscherrerinstitute/eco/tree/bernina-op)


