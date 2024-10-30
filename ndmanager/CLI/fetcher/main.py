"""Entry point for the ndf command"""

import argparse as ap

from ndmanager.CLI.fetcher.install import NdfInstallCommand
from ndmanager.CLI.fetcher.listlibs import NdfListCommand
from ndmanager.CLI.fetcher.remove import NdfRemoveCommand

parser = ap.ArgumentParser(
    prog="ndf",
    description="Manage your ENDF6 format nuclear data libraries",
)
subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)
NdfInstallCommand.parser(subparsers)
NdfListCommand.parser(subparsers)
NdfRemoveCommand.parser(subparsers)


def main() -> None:
    """Entry point for the ndf command"""
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
