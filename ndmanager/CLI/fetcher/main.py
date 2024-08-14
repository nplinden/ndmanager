import argparse as ap

from ndmanager.CLI.fetcher.info import info
from ndmanager.CLI.fetcher.install import install
from ndmanager.CLI.fetcher.listlibs import listlibs
from ndmanager.CLI.fetcher.remove import remove


def main():
    parser = ap.ArgumentParser(
        prog="ndf",
        description="Manage your ENDF6 format nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # install
    install_parser = subparsers.add_parser(
        "install",
        help="Download ENDF6 files from the IAEA website",
    )
    install_parser.add_argument(
        "libraries",
        action="extend",
        nargs="+",
        type=str,
        help="List of nuclear data libraries to download",
    )
    install_parser.add_argument(
        "-s",
        "--sub",
        action="extend",
        nargs="+",
        type=str,
        help="List of sublibraries libraries to download",
    )
    install_parser.set_defaults(func=install)

    # list
    list_parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    list_parser.set_defaults(func=listlibs)

    # info
    info_parser = subparsers.add_parser(
        "info", help="Get info on a nuclear data libary"
    )
    info_parser.add_argument(
        "library",
        type=str,
        action="extend",
        nargs="+",
        help="Name of the desired library",
    )
    info_parser.set_defaults(func=info)

    # remove
    remove_parser = subparsers.add_parser(
        "remove", help="Remove one or more installed ENDF6 libraries"
    )
    remove_parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries to remove",
        action="extend",
        nargs="+",
    )
    remove_parser.set_defaults(func=remove)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
