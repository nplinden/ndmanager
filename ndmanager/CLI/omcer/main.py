"""Entry point for the `ndo` command"""

import argparse as ap

from ndmanager.CLI.omcer.build import NdoBuildCommand
from ndmanager.CLI.omcer.clone import NdoCloneCommand
from ndmanager.CLI.omcer.edit import NdoSn301Command
from ndmanager.CLI.omcer.install import NdoInstallCommand
from ndmanager.CLI.omcer.listlibs import NdoListCommand
from ndmanager.CLI.omcer.remove import NdoRemoveCommand


parser = ap.ArgumentParser(
    prog="ndo",
    description="Manage your OpenMC HDF5 nuclear data libraries",
)
subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

NdoCloneCommand.parser(subparsers)
NdoListCommand.parser(subparsers)
NdoInstallCommand.parser(subparsers)
NdoRemoveCommand.parser(subparsers)
NdoBuildCommand.parser(subparsers)
NdoSn301Command.parser(subparsers)


def main():
    """Entry point for the ndo command"""
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
