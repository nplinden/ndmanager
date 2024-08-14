import argparse as ap
import os
import shutil

from ndmanager.API.data import OPENMC_NUCLEAR_DATA
from ndmanager.CLI.omcer.download import download
from ndmanager.CLI.omcer.generate import chain, generate
from ndmanager.CLI.omcer.substitute import replace_negatives_in_lib


def ndo_sn301(args: ap.Namespace):
    target = OPENMC_NUCLEAR_DATA / args.target / "cross_sections.xml"
    sources = [OPENMC_NUCLEAR_DATA / s / "cross_sections.xml" for s in args.sources]
    replace_negatives_in_lib(target, sources, 301, dryrun=args.dryrun, verbose=True)


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


def ndo_build(args: ap.Namespace):
    generate(args.filename, args.dryrun)


def ndo_install(args: ap.Namespace):
    for lib in args.library:
        download(lib)
