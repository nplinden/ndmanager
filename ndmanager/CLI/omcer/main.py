"""Entry point for the `ndo` command"""

import argparse as ap

from ndmanager.CLI.omcer.build import build_parser
from ndmanager.CLI.omcer.clone import clone_parser
from ndmanager.CLI.omcer.edit import sn301_parser
from ndmanager.CLI.omcer.install import install_parser
from ndmanager.CLI.omcer.listlibs import listlibs_parser
from ndmanager.CLI.omcer.remove import remove_parser


def main():
    """Entry point for the ndo command"""
    parser = ap.ArgumentParser(
        prog="ndo",
        description="Manage your OpenMC HDF5 nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    clone_parser(subparsers)
    listlibs_parser(subparsers)
    install_parser(subparsers)
    remove_parser(subparsers)
    build_parser(subparsers)
    sn301_parser(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
