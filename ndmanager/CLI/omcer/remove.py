import argparse as ap
import shutil

from ndmanager.data import OPENMC_NUCLEAR_DATA


def remove_parser(subparsers):
    parser = subparsers.add_parser("remove", help="Remove one or more OpenMC libraries")
    parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=remove)


def remove(args: ap.Namespace):
    libraries = [OPENMC_NUCLEAR_DATA / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)
