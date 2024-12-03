"""Definition and parser for the `ndo remove` command"""

import argparse as ap
import shutil

from ndmanager.env import NDMANAGER_HDF5
from ndmanager.CLI.parser import Command


class NdoRemoveCommand(Command):
    """Define the `ndo remove` command"""

    @classmethod
    def parser(cls, subparsers) -> None:
        """Add the parser for the 'ndo remove' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "remove", help="Remove one or more OpenMC libraries"
        )
        parser.add_argument(
            "library",
            type=str,
            help="Names of the libraries",
            action="extend",
            nargs="+",
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """Uninstall an OpenMC library

        Args:
            args (ap.Namespace): The argparse object containing the command line argument
        """
        libraries = [NDMANAGER_HDF5 / lib for lib in args.library]
        for library in libraries:
            if library.exists():
                shutil.rmtree(library)
