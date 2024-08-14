A tool to manage your nuclear data libraries.

## Installation

You can install NDManager with `pip`:
```bash
pip install git+https://github.com/nplinden/ndmanager.git
```

## CLI

### Nuclear Data Fetcher `ndf`

Nuclear Data Fetcher `ndf` is a command to manage your evaluated nuclear 
data files in the ENDF6 format.
The spirit of `ndf` is to be used as a kind of package manager for nuclear
data libraries.

As such, `ndf` allows you to download a number of libraries from the 
[IAEA website](https://www-nds.iaea.org/public/download-endf/), to clone them
or uninstall them.

To get a list of all available libraries, you can use the `ndf list` commands, yielding:
```text
jeff33   JEFF-3.3        [✓]: Version 3.3 of the Joint Evaluated Fission and Fusion (JEFF) library distributed by
                              OECD's Nuclear Energy Agency (NEA)
jeff311  JEFF-3.1.1      [ ]: Version 3.1.1 of the Joint Evaluated Fission and Fusion (JEFF) library distributed by
                              OECD's Nuclear Energy Agency (NEA)
jendl5   JENDL-5-Aug2023 [✓]: Version 5 of the Japanese Evaluated Nuclear Data Library (JENDL)library distributed by
                              JAEA
endfb71  ENDF-B-VII.1    [ ]: Version 7.1 of the ENDF-B data library distributed by the NNDC
endfb8   ENDF-B-VIII.0   [✓]: Version 8.0 of the ENDF-B data library distributed by the NNDC
tendl19  TENDL-2019      [✓]: 2019 release of the TENDL library distributed by the Paul Scherrer Institute
                              (Switzerland).
tendl23  TENDL-2023      [ ]: 2023 release of the TENDL library distributed by the Paul Scherrer Institute
                              (Switzerland).
cendl32  CENDL-3.2       [✓]: Version 3.2 of the Chinese Evaluated Nuclear Data Library (CENDL) distributed by the
                              China Nuclear Data Center.
cendl31  CENDL-3.1       [✓]: Version 3.1 of the Chinese Evaluated Nuclear Data Library (CENDL) distributed by the
                              China Nuclear Data Center.
```
All libraries are shown with a shorthand name, used throughout `ndmanager`, as well as a 
fancy name under which the libraries are stored on IAEA's website. 
`ndf list` also provides a short description of the libraries as well as an indication whether
the libraries are installed on your machine or not.

To download and manage libraries, you need to define a directory in which they will be stored,
this can be done by defining the `ENDF6_PATH` environment variable, for example:
```bash
export ENDF6_PATH=~/endf6
```
Make sure that the path stored in `ENDF6_PATH` is writable if you intend to download additional
libraries.
Before downloading a library you may want to get information on it, this can be achieved
the `ndf info` command.
Here is a sample output when querying information from `endfb8`:
```
--------------------------------------------------------------------------  endfb8  --------------------------------------------------------------------------
Fancy name:               ENDF-B-VIII.0
Source:                   https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0
Homepage:                 https://www.nndc.bnl.gov/endf-b8.0/
Available Sublibraries:   ard  d  decay  e  g  he3  he4  n  nfpy  p  photo  sfpy  std  t  tsl
Index:                    1 NSUB=0       Materials:163   Size:222Mb   Zipped:57Mb     20.MeV-150.MeV   [G]     Photo-Nuclear Data
                          2 NSUB=3       Materials:100   Size:88Mb    Zipped:36Mb     100.GeV          [PHOTO] Photo-Atomic Interaction Data
                          3 NSUB=4       Materials:3821  Size:66Mb    Zipped:14Mb                      [DECAY] Radioactive Decay Data
                          4 NSUB=5       Materials:9     Size:2Mb     Zipped:297Kb                     [S/FPY] Spontaneous Fission Product Yields
                          5 NSUB=6       Materials:100   Size:9Mb     Zipped:2Mb      100.GeV          [ARD]   Atomic Relaxation Data
                          6 NSUB=10      Materials:557   Size:2Gb     Zipped:329Mb    20.MeV-200.MeV   [N]     Incident-Neutron Data
                          7 NSUB=11      Materials:31    Size:7Mb     Zipped:2Mb      20.MeV           [N/FPY] Neutron-Induced Fission Product Yields
                          8 NSUB=12      Materials:34    Size:230Mb   Zipped:65Mb     5.eV             [TSL]   Thermal Neutron Scattering Data
                          9 NSUB=19      Materials:11    Size:65Mb    Zipped:21Mb     20.MeV-150.MeV   [Std]   Neutron Cross Section Standards
                          10 NSUB=113    Materials:100   Size:27Mb    Zipped:8Mb      100.GeV          [E]     Electro-Atomic Interaction Data
                          11 NSUB=10010  Materials:49    Size:54Mb    Zipped:14Mb     2.MeV-150.MeV    [P]     Incident-Proton Data
                          12 NSUB=10020  Materials:5     Size:414Kb   Zipped:97Kb     1.MeV-30.MeV     [D]     Incident-Deuteron Data
                          13 NSUB=10030  Materials:5     Size:736Kb   Zipped:164Kb    20.MeV           [T]     Incident-Triton Data
                          14 NSUB=20030  Materials:3     Size:810Kb   Zipped:194Kb    20.MeV           [HE3]   Incident-He3 data
                          15 NSUB=20040  Materials:1     Size:9Kb     Zipped:3Kb      20.MeV           [HE4]   Incident-Alpha data

                          Total: Materials:4989  Size:2Gb     Zipped:546Mb
--------------------------------------------------------------------------------------------------------------------------------------------------------------
```

Finally, to download a library you can use the `ndf install` command, 
multiple libraries can be installed at the same time:
```
ndf install jeff33 cendl32
```

### OpenMC data management `ndo`