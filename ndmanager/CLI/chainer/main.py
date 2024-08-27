"""Entry point for the ndc command"""

import argparse as ap

from ndmanager.CLI.chainer.build import build_parser
from ndmanager.CLI.chainer.install import install_parser
from ndmanager.CLI.chainer.listchains import list_parser
from ndmanager.CLI.chainer.remove import remove_parser


def main():
    """Entry point for the ndc command"""
    parser = ap.ArgumentParser(
        prog="ndo",
        description="Manage your OpenMC HDF5 nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    build_parser(subparsers)
    list_parser(subparsers)
    install_parser(subparsers)
    remove_parser(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
