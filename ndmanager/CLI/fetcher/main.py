"""Entry point for the ndf command"""

import argparse as ap

from ndmanager.CLI.fetcher.info import info_parser
from ndmanager.CLI.fetcher.install import install_parser
from ndmanager.CLI.fetcher.listlibs import listlibs_parser
from ndmanager.CLI.fetcher.remove import remove_parser


def main() -> None:
    """Entry point for the ndf command"""
    parser = ap.ArgumentParser(
        prog="ndf",
        description="Manage your ENDF6 format nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    install_parser(subparsers)
    listlibs_parser(subparsers)
    info_parser(subparsers)
    remove_parser(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
