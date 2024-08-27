"""Definition and parser for the `ndo remove` command"""

import argparse as ap
import shutil

from ndmanager.data import NDMANAGER_CHAINS


def remove_parser(subparsers):
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
    parser.set_defaults(func=remove)


def remove(args: ap.Namespace):
    """Uninstall an OpenMC library

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    chains = [NDMANAGER_CHAINS / chain for chain in args.chains]
    for chain in chains:
        if chain.exists():
            shutil.rmtree(chain)
