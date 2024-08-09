import argparse as ap

from ndmanager.CLI.fetcher import (ndf_avail, ndf_clone, ndf_info, ndf_install,
                                   ndf_list, ndf_remove)


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
    install_parser.set_defaults(func=ndf_install)

    # avail
    avail_parser = subparsers.add_parser("avail", help="List installed ENDF6 libraries")
    avail_parser.set_defaults(func=ndf_avail)

    # list
    list_parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    list_parser.set_defaults(func=ndf_list)

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
    info_parser.set_defaults(func=ndf_info)

    # clone
    clone_parser = subparsers.add_parser(
        "clone", help="Clone an installed ENDF6 library"
    )
    clone_parser.add_argument(
        "source",
        type=str,
        help="Name for the original library",
    )
    clone_parser.add_argument(
        "target",
        type=str,
        help="Name for the new cloned library",
    )
    clone_parser.set_defaults(func=ndf_clone)

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
    remove_parser.set_defaults(func=ndf_remove)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
