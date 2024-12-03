"""Entry point for the ndc command"""

import argparse as ap

from ndmanager.CLI.chainer.build import NdcBuildCommand
from ndmanager.CLI.chainer.install import NdcInstallCommand
from ndmanager.CLI.chainer.listchains import NdcListCommand
from ndmanager.CLI.chainer.remove import NdcRemoveCommand


parser = ap.ArgumentParser(
    prog="ndo",
    description="Manage your OpenMC HDF5 nuclear data libraries",
)
subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

NdcBuildCommand.parser(subparsers)
NdcInstallCommand.parser(subparsers)
NdcListCommand.parser(subparsers)
NdcRemoveCommand.parser(subparsers)


def main():
    """Entry point for the ndc command"""
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
