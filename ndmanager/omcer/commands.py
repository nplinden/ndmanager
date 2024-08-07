import argparse as ap
import os
from ndmanager.data import OPENMC_NUCLEAR_DATA, NDM_DIR
from ndmanager.fetcher.download import download
from ndmanager.omcer.generate import chain, generate
from ndmanager.omcer.substitute import replace_negatives_in_lib
from ndmanager.omcer.download import download
import shutil

def ndo_sn301(args: ap.Namespace):
    target = OPENMC_NUCLEAR_DATA / args.target / "cross_sections.xml"
    sources = [OPENMC_NUCLEAR_DATA / s / "cross_sections.xml" for s in args.sources]
    replace_negatives_in_lib(
        target, sources, 301, dryrun=args.dryrun, verbose=True
    )


def ndo_clone(args: ap.Namespace):
    source = OPENMC_NUCLEAR_DATA / args.source
    target = OPENMC_NUCLEAR_DATA / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)


def ndo_remove(args: ap.Namespace):
    libraries = [OPENMC_NUCLEAR_DATA / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)


def ndo_avail(*args):
    col, _ = os.get_terminal_size()
    print(f"{'  OpenMC HDF5 Libraries  ':{'-'}{'^'}{col}}")
    toprint = "  ".join([p.name for p in OPENMC_NUCLEAR_DATA.glob("*")])
    print(toprint)
    print("\n\n")


def ndo_build(args: ap.Namespace):
    if args.chain is not None:
        print("Processing chain file")
        chain(args.filename)
    generate(args.filename, args.dryrun)

def ndo_path(args: ap.Namespace):
    p = OPENMC_NUCLEAR_DATA / args.library / "cross_sections.xml"
    if not p.exists():
        raise ValueError("Library cross_sections.xml file does not exist")
    else:
        print(str(p))

def ndo_get(args: ap.Namespace):
    target = OPENMC_NUCLEAR_DATA / args.library / "cross_sections.xml"
    if target.exists():
        print(target)
    else:
        raise ValueError(f"{args.library} not found")

def ndo_install(args: ap.Namespace):
    for lib in args.library:
        download(lib)
