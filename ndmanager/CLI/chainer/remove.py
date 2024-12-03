"""Definition and parser for the `ndo remove` command"""

import argparse as ap

from ndmanager.env import NDMANAGER_CHAINS
from ndmanager.data import OPENMC_CHAINS
from ndmanager.CLI.parser import Command


class NdcRemoveCommand(Command):
    """Define the `ndc remove` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndc remove' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser("remove", help="Remove one or more OpenMC chain")
        parser.add_argument(
            "chains",
            type=str,
            help="Names of the chain",
            action="extend",
            nargs="+",
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """Uninstall an OpenMC library

        Args:
            args (ap.Namespace): The argparse object containing the command line argument
        """
        for chain in args.chains:
            if chain in OPENMC_CHAINS:
                p = NDMANAGER_CHAINS / "official" / f"{chain}.xml"
            else:
                p = NDMANAGER_CHAINS / f"{chain}.xml"
            p.unlink()
