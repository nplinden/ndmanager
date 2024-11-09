# NDManager

[![Coverage
Status](https://coveralls.io/repos/github/nplinden/ndmanager/badge.svg?branch=develop)](https://coveralls.io/github/nplinden/ndmanager?branch=develop)

NDManager is a python package that helps you manage your nuclear data
files in a clean manner.

It provides an API and a CLI for creating and interacting with a
database of ENDF6 files, as well as processed data files and depletion
chain files in the OpenMC format.

In addition, it encapsulate the
[sandy](https://github.com/luca-fiorito-11/sandy) nuclear data sampling
tool to help you easily generate perturbed files in the OpenMC HDF5
format.

Full documentation is available
[here](https://ndmanager.readthedocs.io/en/latest/).

## Installation

NDManager is available on [PyPI](https://pypi.org/project/ndmanager/)
and can therefore be installed with `pip`:

```console
$ pip install ndmanager
```

There are however a few caveats regarding the dependencies of NDManager.
To build processed nuclear data files in the OpenMC HDF5 format, an
installation of the [NJOY](https://github.com/njoy/NJOY2016) processing
code as well as the [OpenMC](https://github.com/openmc-dev/openmc)
python API is required. These can't be installed with pip so you will
need to install them separately.

NDManager also uses sandy to generate perturbed data files, currently
the prefered version is `v1.1` and is not available on PyPI, you can
install it manually with to following command:

```console
$ pip install git+https://github.com/luca-fiorito-11/sandy.git@v1.1
```

## Configuration

NDManager allows you to manage databases for different kinds of files:

* ENDF6 evaluation nuclear data files 
* HDF5 processed nuclear data files 
* XML depletion chain files 
* HDF5 sampled nuclear data files

The directories in which these databases will be stored can be specified
using the following environment variables: `NDMANAGER_ENDF6`,
`NDMANAGER_HDF5`, `NDMANAGER_CHAINS`, `NDMANAGER_SAMPLES`.

You can also define these paths in a YAML file located at
`$HOME/.config/ndmanager/settings.yml`:

``` yaml
NDMANAGER_ENDF6: /path/to/endf6
NDMANAGER_HDF5: /path/to/hdf5
NDMANAGER_CHAINS: /path/to/chains
NDMANAGER_SAMPLES: /path/to/samples
```

If no path is set, the data will be stored in `$HOME/.config/ndmanager`

## Using NDManager

The following sections give a quick overview of the main features of NDManager's modules.

### The Fetcher Module `ndf`

The `ndf` module acts as a kind of package manager for evaluated nuclear
data files. It uses the [IAEA
ENDF-Archive](https://www-nds.iaea.org/public/download-endf/) as an
online source of ENDF6 files.

Most of the libraries in this repo have a common directory structure
making them easy to parse. You can list the available libraries using
the `ndf list` command:

```console
$ ndf list
----------------------------------------------------  Available libraries  ----------------------------------------------------
brond22              BROND-2-2            [ ]: BROND-2 USSR evaluated neutron data library, issued in 1992
brond31              BROND-3.1            [✓]: BROND-3.1 Russian evaluated neutron data library, issued in 2016
cendl31              CENDL-3.1            [ ]: CENDL-3.1 Chinese evaluated neutron data library, issued in 2009
cendl32              CENDL-3.2            [ ]: CENDL-3.2 Chinese evaluated neutron data library, issued in 2020
endfb70              ENDF-B-VII.0         [ ]: ENDF/B-VII.0 U.S. Evaluated Nuclear Data Library, issued in 2006
endfb71              ENDF-B-VII.1         [ ]: ENDF/B-VII.1 U.S. Evaluated Nuclear Data Library, issued in 2011
endfb8               ENDF-B-VIII.0        [✓]: ENDF/B-VIII.0 U.S. Evaluated Nuclear Data Library, issued in 2018
endfb81              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S. Evaluated Nuclear Data Library, issued in 2024
fendl32b             FENDL-3.2b           [ ]: FENDL-3.2b Fusion Evaluated Nuclear Data Library, 2022
jeff31               JEFF-3.1             [ ]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
jeff311              JEFF-3.1.1           [✓]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
jeff312              JEFF-3.1.2           [ ]: JEFF-3.1.2 Evaluated nuclear data library of the OECD Nuclear Energy Agency
jeff33               JEFF-3.3             [✓]: JEFF-3.3 Evaluated nuclear data library of the OECD Nuclear Energy Agency, 2017
jendl32              JENDL-3.2            [ ]: JENDL-3.2 Japanese evaluated nuclear data library, 1994
jendl4               JENDL-4.0            [ ]: JENDL-4.0 Japanese evaluated nuclear data library, 2010
jendl5               JENDL-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data library, 2021
tendl2021            TENDL-2021           [ ]: TENDL-2021 TALYS-based Evaluated Nuclear Data Library, 2021
tendl2023            TENDL-2023           [✓]: TENDL-2023 TALYS-based Evaluated Nuclear Data Library, 2023
-------------------------------------------------------------------------------------------------------------------------------
```

The first time you run this command, the entire IAEA database will be parsed, this can take about a minute.
Subsequent runs of the `ndf list` command will reuse the cached information so it should go much faster.

By default the `list` command shows a subset of what is available on the website, and shows you a convenient short name in the first column.
To get the entire list of available libraries you can add the `--all` tag to the command.

You can then install any library you want with the `ndf install` command, providing a `-j` tag followed by an integer allows you parallelize the process:

```console
$ ndf install jeff33 -j 10
JEFF-3.3/n               : 100%|████████████████████████████████████████| 562/562 [00:12s]
JEFF-3.3/decay           : 100%|████████████████████████████████████████| 3852/3852 [00:23s]
JEFF-3.3/nfpy            : 100%|████████████████████████████████████████| 19/19 [00:00s]
JEFF-3.3/sfpy            : 100%|████████████████████████████████████████| 3/3 [00:00s]
JEFF-3.3/tsl             : 100%|████████████████████████████████████████| 20/20 [00:03s]
```

The `ndf remove` command will help you uninstall libraries you don't need anymore.

You can use NDManager's python API to get the path to an ENDF6 tape installed using `ndf`:

```python
import ndmanager
tape = ndmanager.get_endf6("jeff33", "n", "Pu239")
```

The second argument refers to the sublibraries.
The ones you will probably care the most about are: 

* `n` for incident neutron data, NSUB=10 
* `photo` for photoatomic interaction, NSUB=3
* `ard` for atomic relaxation data, NSUB=6
* `tsl` for thermal scattering laws, NSUB=12

### The Omcer Module `ndo`

The Omcer module is your tool to manage processed nuclear data files in the OpenMC HDF5 format.

```yaml
# jeff33.yml
summary: A library based on the JEFF-3.3 evaluations.
description: |
  This defines a library based on the JEFF-3.3 evaluations for
  neutron cross-sections and thermal scattering laws, and on
  ENDF-B/VIII.0 for gamma photoatomic reactions and atomic
  relaxation.

  Some evaluations from other libraries are used instead
  or in addition to JEFF-3.3 evaluations:
  C0:     JEFF-3.3 contains C0 and C13 isotopes of carbon. Since
          using C0 can cause some issues running the same problem
          with multiple libraries, I prefer to remove them and
          use ENDF-B/VIII.0 carbon instead. Normally you would also
          build TSL libraries using C0, I substitute it for C12.
  C12:    See C0
  C13:    See C0. 
  Ta180:  OpenMC wrongly defines natural Ta as containing Ta180
          instead of Ta180M because ENDF-B/VIII.0 has no Ta180M
          evaluation. Since JEFF-3.3 has no Ta180, materials
          containing Ta will crash simulations.
  O17:    The O17 evaluation of JEFF-3.3 is faulty. I use the ENDF-B/VIII.0
          evaluation instead.
name: jeff33 # The name of the future HDF5 library
neutron:
  base: jeff33 # The ENDF6 library to use the tapes from by default
  temperatures: 250 294 600 900 1200 2500
  ommit: C0 # The C0 tape from the base library will be ignored
  add: # If added nuclides already exist in the base library, they will be replaced
    endfb8: Ta180 C12 C13 O17
photon: # The base library need at least photoatomic tapes, ard tapes are optionnal
  base: endfb8
tsl:
  base: jeff33
  add:
    jeff33:
      tsl_0031_Graphite.endf6: C12 # Here I specify that the graphite TSL laws must be 
                                   # built using the C12 incident neutron file, specified
                                   # in the "neutron" section as coming from endf8
```

Running the `ndo build` command on this file will build your library, once again the `-j` tag allows you
to parallelize the process:

```console
$ ndo build jeff33.yml -j 40
```

This will build the HDF5 file for all nuclides and create a `cross_sections.xml` file that you can provide to OpenMC to use the library.

Sometimes you may want to substitute a single nuclide from a library, for instance to check the impact of a new evaluation of your favorite nuclide.
My favorite nuclide is Cl35, and it turns out that the cross-sections of Cl35 in JEFF-3.3 and JENDL-5.0 are very different in the fast domain.

To check the impact of substituting the JENDL-5.0 cross-section in my JEFF-3.3 library, I can write the following input file:

```yaml
summary: The JEFF-3.3 library with the JENDL-5.0 Cl35 data
description: |
    This library reuses the cross-sections available in the jeff33 processed nuclear
    data library available in the NDManager database, and substitute the Cl35 file with
    a new one created from the JENDL-5.0 ENDF6 tape.
name: jeff33-jendl5-Cl35
neutron:
    reuse: jeff33 # This needs to be the name of an HDF5 library installed with Omcer
    temperatures: 250 294 600 900 1200 2500
    add:
        jendl5: Cl35
photon:
    reuse: jeff33
```

This will run NJOY to create a new processed file only for Cl35.
The `cross_sections.xml` file will point to the jeff33 processed library for all other nuclides.

To use your new library with OpenMC you can use NDManager's python API:

```python
from ndmanager.API.openmc import set_nuclear_data
set_nuclear_data("jeff33")

# Proceed with openmc stuff
```

In addition to creating your own libraries, you can download to ones provided by the [official OpenMC website](https://openmc.org/data-libraries/):

```console
$ ndo list
--------------------------------------------------  Installable Libraries  ---------------------------------------------------
official/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC library based on ENDF-B/VII.1
official/endfb8  ENDF-B/VIII.0   [ ]: Official OpenMC library based on ENDF-B/VIII.0
official/jeff33  JEFF-3.3        [ ]: Official OpenMC library based on JEFF-3.3
lanl/endfb70     ENDF-B/VII.0    [ ]: ENDF-B/VII.0 based library converted from ACE files distributed with MCNP5/6
lanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 based library converted from ACE files distributed with MCNP5/6
lanl/endfb8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from ACE files distributed by Los Alamos National
                                      lab (LANL)
$ ndo install official/endfb8
Downloading official/endfb8: 100%|████████████████████████████████████████| 3.15G/3.15G [02:03s]
Extracting  official/endfb8: 100%|███████████████████████████████████████▉| 12.7G/12.7G [02:17s]
```

And then in a python script

```python
from ndmanager.API.openmc import set_nuclear_data
set_nuclear_data("official/endfb8")

# Proceed with openmc stuff
```

### The Chainer Module `ndc`

The Chainer module work in a very similar way to the Omcer module.
Here's what a typical `ndc` input file looks like:

```yaml
name: jeff33/fast
description: |
  A depletion chain based on the JEFF-3.3 evaluations.
branching_ratios: sfr
n:
  base: jeff33
  ommit: C0
  add:
    endfb8: Ta180 C12 C13 O17
decay: 
  base: jeff33
nfpy:
  base: jeff33
```

You can run the `ndc build` command to generate the XML chain file.
To use the generated chains you can use NDManager's python API:

```python
from ndmanager.API.openmc import set_chain
set_chain("jeff33/fast")

# Proceed with openmc stuff
```

To set both the cross-section files and the chain file at the same time:

```python
from ndmanager.API.openmc import set_nuclear_data
set_nuclear_data("jeff33", "jeff33/fast")

# Proceed with openmc stuff
```
 Finally, you can download the official chain from the OpenMC website:

 ```console
 $ ndc list
 ----------------------------------------  Installable Chains  ----------------------------------------
endfb71/thermal  [ ]: A chain based on the ENDF-B/VII.1 evaluation with thermal capture branching
                       ratios
endfb71/fast     [ ]: A chain based on the ENDF-B/VII.1 evaluation with fast capture branching ratios
endfb8/thermal   [ ]: A chain based on the ENDF-B/VIII.0 evaluation with thermal capture branching
                       ratios
endfb8/fast      [ ]: A chain based on the ENDF-B/VIII.0 evaluation with thermal capture branching
                       ratios
casl/thermal     [ ]: A simplified chain as described by https://doi.org/10.2172/1256820 with thermal
                       capture branching ratios
casl/fast        [ ]: A simplified chain as described by https://doi.org/10.2172/1256820 with fast
                       capture branching ratios
 $ ndc install endfb8/fast
 Downloading endfb8/fast    : 100%|████████████████████████████████████████| 26.3M/26.3M [00:01s]
```
