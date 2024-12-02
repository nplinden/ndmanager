"""The entry point for the `nds` command"""

import argparse as ap

from ndmanager.CLI.sampler.cov import NdsCovCommand
from ndmanager.CLI.sampler.hdf5 import NdsHdf5Sampling
from ndmanager.CLI.sampler.pendf import NdsPendfCommand
from ndmanager.CLI.sampler.remove import NdsRemoveCommand
from ndmanager.CLI.sampler.listsamples import NdsListCommand

parser = ap.ArgumentParser(prog="nds", description="Sample your nuclear data")
subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)
NdsPendfCommand.parser(subparsers)
NdsRemoveCommand.parser(subparsers)
NdsCovCommand.parser(subparsers)
NdsHdf5Sampling.parser(subparsers)
NdsListCommand.parser(subparsers)


def main() -> None:
    """Entry point for the nds command"""
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
