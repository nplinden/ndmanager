A tool to download ENDF6 nuclear data files from the [IAEA website](https://www-nds.iaea.org/public/download-endf/).

## Installation

You can install NDManager with `pip`:
```bash
pip install git+https://github.com/nplinden/ndmanager.git
```

## Examples

You can use the `ndfetch` command to download ENDF6 nuclear data files.

To download all available sublibraries from JEFF-3.3:

```bash
ndfetch jeff33
```

To download a specific set of sublibraries from ENDF-B/VIII.0:

```bash
ndfetch endfb8 decay sfpy
```

Running those two commands in the same directory will result in the following
directory structure:

```
endf6
├── endfb8
│   ├── decay
│   └── sfpy
└─── jeff33
    ├── decay
    ├── n
    ├── nfpy
    ├── sfpy
    └── tsl
```

You can then set the `$ENDF6_PATH` environment variable to the top directory's
path to use the `ndfind` command. This command will search for nuclear data file
paths for you:

```bash
$ ndfind jeff33 n Pu239
/home/nlinden/workspace/NuclearData/endf6/jeff33/n/n_9437_94-Pu-239.dat
```