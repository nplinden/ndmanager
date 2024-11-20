"""Definition and parser for the 'nds remove' command"""

import argparse as ap
import shutil

from ndmanager.env import NDMANAGER_SAMPLES


class NdsRemoveCommand:
    """Define the `nds remove` command"""

    def __init__(self, args: ap.Namespace) -> None:
        """Execute the `nds remove` command given an argparse namespace

        Args:
            args (ap.Namespace): An argparse namespace containing the `nds remove`
                                 arguments
        """
        libraries = [NDMANAGER_SAMPLES / lib for lib in args.library]
        for library in libraries:
            if library.exists():
                shutil.rmtree(library)

    @classmethod
    def parser(cls, subparsers):
        """Add the parser for the 'nds remove' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "remove", help="Remove one or more installed sampled libraries"
        )
        parser.add_argument(
            "library",
            type=str,
            help="Names of the libraries to remove",
            action="extend",
            nargs="+",
        )
        parser.set_defaults(func=cls)
