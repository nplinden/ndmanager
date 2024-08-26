"""Definition and parser for the `ndo install` command"""

import argparse as ap
import shutil
import subprocess as sp
import tempfile
from contextlib import chdir
from pathlib import Path

from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.data import (NDMANAGER_MODULEPATH, OPENMC_LIBS,
                            OPENMC_NUCLEAR_DATA)


def install_parser(subparsers):
    """Add the parser for the 'ndo build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "install", help="Install one or more OpenMC libraries"
    )
    parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=install)


def install(args: ap.Namespace):
    """Download and install a OpenMC nuclear data library from the official website

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    for libname in args.library:
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                family, lib = libname.split("/")
                dico = OPENMC_LIBS[family][lib]
                sp.run(["wget", "-q", "--show-progress", dico["source"]], check=True)
                sp.run(["tar", "xf", dico["tarname"]], check=True)

                source = Path(dico["extractedname"])
                target = OPENMC_NUCLEAR_DATA / family / lib
                target.parent.mkdir(exist_ok=True, parents=True)
                shutil.rmtree(target, ignore_errors=True)
                shutil.move(source, target)

    if NDMANAGER_MODULEPATH is not None:
        xs_modulefile(f"xs/{family}-{lib}", dico["info"], target / "cross_sections.xml")
