import argparse as ap

from ndmanager.fetcher import ndf_install, ndf_avail, ndf_info, ndf_clone, ndf_remove, ndf_list
from ndmanager.omcer import ndb_list, ndb_clone, ndb_remove, ndb_build, ndb_sn301, ndb_path


def ndf():
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
    install_parser.add_argument("libraries",
                                 action="extend",
                                 nargs="+",
                                 type=str,
                                 help="List of nuclear data libraries to download"
                                 )
    install_parser.add_argument("-s",
                                 "--sub",
                                 action="extend",
                                 nargs="+",
                                 type=str,
                                 help="List of sublibraries libraries to download"
                                 )
    install_parser.set_defaults(func=ndf_install)

    # avail
    avail_parser = subparsers.add_parser(
        "avail",
        help="List installed ENDF6 libraries"
    )
    avail_parser.set_defaults(func=ndf_avail)

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List libraries compatible with NDManager"
    )
    list_parser.set_defaults(func=ndf_list)

    # info
    info_parser = subparsers.add_parser(
        "info",
        help="Get info on a nuclear data libary"
    )
    info_parser.add_argument(
        "library",
        type=str,
        action="extend",
        nargs="+",
        help="Name of the desired library"
    )
    info_parser.set_defaults(func=ndf_info)

    # clone
    clone_parser = subparsers.add_parser(
        "clone",
        help="Clone an installed ENDF6 library"
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
        "remove",
        help="Remove one or more installed ENDF6 libraries"
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

def ndb():
    parser = ap.ArgumentParser(
        prog="ndb",
        description="Manage your OpenMC HDF5 nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List installed libraries"
    )
    list_parser.set_defaults(func=ndb_list)

    # clone
    clone_parser = subparsers.add_parser(
        "clone",
        help="Clone an installed OpenMC library"
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
    clone_parser.set_defaults(func=ndb_clone)

    # remove
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove one or more OpenMC libraries"
    )
    remove_parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    remove_parser.set_defaults(func=ndb_remove)

    # build
    build_parser = subparsers.add_parser(
        "build",
        help="Build an OpenMC library from a YAML input file"
    )
    build_parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target library"
    )
    build_parser.add_argument(
        "--dryrun",
        help="Do not perform NJOY runs",
        action="store_true"
    )
    build_parser.add_argument(
        "--chain",
        help="Builds the depletion chain",
        action="store_true"
    )
    build_parser.set_defaults(func=ndb_build)

    # sn301
    sn301_parser = subparsers.add_parser(
        "sn301",
        help="Substitute negative MT=301 cross-section in HDF5 library"
    )
    sn301_parser.add_argument(
        "--target",
        "-t",
        type=str,
        help="The library to fix"
    )
    sn301_parser.add_argument(
        "--sources",
        "-s",
        action="extend",
        nargs="+",
        type=str,
        help="List of nuclear data libraries to choose from"
    )
    sn301_parser.add_argument(
        "--dryrun",
        help="Do not perform the substitution",
        action="store_true"
    )
    sn301_parser.set_defaults(func=ndb_sn301)

    # info
    path_parser = subparsers.add_parser(
        "path",
        help="Get path to the library's cross_section.xml file"
    )
    path_parser.add_argument(
        "library",
        type=str,
        help="Name of the desired library"
    )
    path_parser.set_defaults(func=ndb_path)


    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()