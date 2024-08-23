"""Definition and parser for the `ndo remove` command"""
import argparse as ap
import shutil

from ndmanager.data import OPENMC_NUCLEAR_DATA


def remove_parser(subparsers):
    """Add the parser for the 'ndo remove' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
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
    """Uninstall an OpenMC library

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    libraries = [OPENMC_NUCLEAR_DATA / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)
