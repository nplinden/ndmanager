"""Definition and parser for the 'ndf remove' command"""

import argparse as ap
import shutil

from ndmanager.data import NDMANAGER_ENDF6


def remove_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndf info' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "remove", help="Remove one or more installed ENDF6 libraries"
    )
    parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries to remove",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=remove)


def remove(args: ap.Namespace):
    """Uninstall a library from the NDManager database

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    libraries = [NDMANAGER_ENDF6 / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)
