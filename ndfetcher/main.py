import argparse as ap
from ndfetcher.commands import download_cmd, generate_cmd, list_cmd, clone_cmd, remove_cmd, sn301_cmd, info_cmd

def main():
    parser = ap.ArgumentParser(
        prog="ndf",
        description="Process ENDF6 files to HDF5 OpenMC ready library files.",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # download
    download_parser = subparsers.add_parser(
        "download",
        help="Download ENDF6 files from the IAEA website.",
    )
    download_parser.add_argument("-l", 
                                "--lib",
                                action="extend",
                                nargs="+",
                                type=str,
                                help="List of nuclear data libraries to download."
                                )
    download_parser.add_argument("-s", 
                                "--sub",
                                action="extend",
                                nargs="+",
                                type=str,
                                help="List of sublibraries libraries to download."
                                )
    download_parser.set_defaults(func=download_cmd)

    #build
    build_parser = subparsers.add_parser(
        "build",
        help="Build a database from a YAML file."
    )
    build_parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target library"
    )
    build_parser.add_argument(
        "--dryrun",
        help="Does not perform NJOY runs.",
        action="store_true"
    )
    build_parser.add_argument(
        "--chain",
        help="Builds the depletion chain.",
        action="store_true"
    )
    build_parser.set_defaults(func=generate_cmd)

    #list
    list_parser = subparsers.add_parser(
        "list",
        help="List available libraries."
    )
    list_parser.add_argument(
        "type",
        type=str,
        nargs="?",
        default="all",
        help="Type of library to choose from endf6 or openmc"
    )
    list_parser.set_defaults(func=list_cmd)

    #info
    info_parser = subparsers.add_parser(
        "info",
        help="Get info the a nuclear data libary"
    )
    info_parser.add_argument(
        "library",
        type=str,
        help="Name of the desired library"
    )
    info_parser.set_defaults(func=info_cmd)


    #clone
    clone_parser = subparsers.add_parser(
        "clone",
        help="Clone an ENDF6 or OpenMC library"
    )
    clone_parser.add_argument(
        "type",
        type=str,
        help="Type of library to choose from endf6 or openmc"
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
    clone_parser.set_defaults(func=clone_cmd)

    #remove
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an ENDF6 or OpenMC library"
    )
    remove_parser.add_argument(
        "type",
        type=str,
        help="Type of library to remove from endf6 or openmc"
    )
    remove_parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    remove_parser.set_defaults(func=remove_cmd)

    #sn301
    sn301_parser = subparsers.add_parser(
        "sn301",
        help="Substitute negative MT=301 in HDF5 library."
    )
    sn301_parser.add_argument(
        "--target",
        "-t",
        type=str,
        help="The library to fix."
    )
    sn301_parser.add_argument(
        "--sources",
        "-s",
        action="extend",
        nargs="+",
        type=str,
        help="List of nuclear data libraries to choose from."
    )
    sn301_parser.add_argument(
        "--dryrun",
        help="Does not perform the substitution.",
        action="store_true"
    )
    sn301_parser.set_defaults(func=sn301_cmd)


    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()