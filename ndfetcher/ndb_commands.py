import argparse as ap
import os
from itertools import product
from ndfetcher.data import NSUB_list, ENDF6_PATH, OMC_LIBRARIES
import numpy as np
from tabulate import tabulate
from multiprocessing import Pool
import time
from ndfetcher.utils import clear_line, print_offset
from ndfetcher.download import download
from ndfetcher.generate import chain, generate
from ndfetcher.substitute import replace_negatives_in_lib
from ndfetcher.data import NDLIBS
import shutil


def ndb_sn301(args: ap.Namespace):
    target = OMC_LIBRARIES / args.target / "cross_sections.xml"
    sources = [OMC_LIBRARIES / s / "cross_sections.xml" for s in args.sources]
    replace_negatives_in_lib(
        target, sources, 301, dryrun=args.dryrun, verbose=True
    )


def ndb_clone(args: ap.Namespace):
    source = OMC_LIBRARIES / args.source
    target = OMC_LIBRARIES / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)


def ndb_remove(args: ap.Namespace):
    libraries = [OMC_LIBRARIES / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)


def ndb_list(*args):
    col, _ = os.get_terminal_size()
    print(f"{'  OpenMC HDF5 Libraries  ':{'-'}{'^'}{col}}")
    toprint = "  ".join([p.name for p in OMC_LIBRARIES.glob("*")])
    print(toprint)
    print("\n\n")


def ndb_build(args: ap.Namespace):
    if args.chain is not None:
        chain(args.filename)
    generate(args.filename, args.dryrun)

def ndb_path(args: ap.Namespace):
    p = OMC_LIBRARIES / args.library / "cross_sections.xml"
    if not p.exists():
        raise ValueError("Library cross_section.xml file does not exist")
    else:
        print(str(p))
