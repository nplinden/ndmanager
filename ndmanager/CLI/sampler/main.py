"""The entry point for the `nds` command"""
import argparse as ap

from ndmanager.CLI.sampler.remove import NdsRemoveCommand
from ndmanager.CLI.sampler.sample import NdsSampleCommand

parser = ap.ArgumentParser(prog="nds", description="Sample your nuclear data")
subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)
NdsSampleCommand.parser(subparsers)
NdsRemoveCommand.parser(subparsers)


def main() -> None:
    """Entry point for the nds command"""
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
