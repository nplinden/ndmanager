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
jeff33   JEFF-3.3        [✓]: Version 3.3 of the Joint Evaluated Fission
                               and Fusion (JEFF) library distributed by OECD's Nuclear Energy Agency (
                              NEA)
jeff311  JEFF-3.1.1      [ ]: Version 3.1.1 of the Joint Evaluated Fissi
                              on and Fusion (JEFF) library distributed by OECD's Nuclear Energy Agency
                               (NEA)
jendl5   JENDL-5-Aug2023 [✓]: Version 5 of the Japanese Evaluated Nuclea
                              r Data Library (JENDL)library distributed by JAEA
endfb71  ENDF-B-VII.1    [ ]: Version 7.1 of the ENDF-B data library dis
                              tributed by the NNDC
endfb8   ENDF-B-VIII.0   [✓]: Version 8.0 of the ENDF-B data library dis
                              tributed by the NNDC
tendl19  TENDL-2019      [✓]: 2019 release of the TENDL library distribu
                              ted by the Paul Scherrer Institute (Switzerland).
tendl23  TENDL-2023      [ ]: 2023 release of the TENDL library distribu
                              ted by the Paul Scherrer Institute (Switzerland).
cendl32  CENDL-3.2       [✓]: Version 3.2 of the Chinese Evaluated Nucle
                              ar Data Library (CENDL) distributed by the China Nuclear Data Center.
cendl31  CENDL-3.1       [✓]: Version 3.1 of the Chinese Evaluated Nucle
                              ar Data Library (CENDL) distributed by the China Nuclear Data Center.
```
All libraries are shown with a shorthand name, used throughout `ndmanager`, as well as a 
fancy name under which the libraries are stored on IAEA's website. 
`ndf list` also provides a short description of the libraries as well as an indication whether
the libraries are installed on your machine or not.

To download and manage libraries, you need to define a directory in which they will be,
this can be done by defining the `ENDF6_PATH` environment variable, for example:
```bash
export ENDF6_PATH=~/endf6
```
Make sure that the path stored in `ENDF6_PATH` is writable if you intend to download additional
libraries.
