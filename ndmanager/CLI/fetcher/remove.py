"""Definition and parser for the 'ndf remove' command"""

import argparse as ap
import shutil

from ndmanager.env import NDMANAGER_ENDF6


class NdfRemoveCommand:
    def __init__(self, args: ap.Namespace) -> None:
        libraries = [NDMANAGER_ENDF6 / lib for lib in args.library]
        for library in libraries:
            if library.exists():
                shutil.rmtree(library)

    @classmethod
    def parser(cls, subparsers):
        """Add the parser for the 'ndf remove' command to a subparser object

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
        parser.set_defaults(func=cls)
