"""Definition and parser for the `ndo clone` command"""

import argparse as ap
import shutil

from ndmanager.env import NDMANAGER_HDF5
from ndmanager.CLI.parser import Command


class NdoCloneCommand(Command):
    """define the `ndo clone` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndo clone' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "clone", help="Clone an installed OpenMC library"
        )
        parser.add_argument(
            "source",
            type=str,
            help="Name for the original library",
        )
        parser.add_argument(
            "target",
            type=str,
            help="Name for the new cloned library",
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """Clone an HDF5 library from the NDManager database

        Args:
            args (ap.Namespace): The argparse object containing the command line argument

        Raises:
            ValueError: The source library does not exist
            ValueError: The target library already exists
        """
        source = NDMANAGER_HDF5 / args.source
        target = NDMANAGER_HDF5 / args.target
        if not source.exists():
            raise ValueError(f"{args.source} is not in the library list.")
        if target.exists():
            raise ValueError(f"{args.target} is already in the library list.")
        shutil.copytree(source, target)
