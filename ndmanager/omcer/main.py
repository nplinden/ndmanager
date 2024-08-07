import argparse as ap

from ndmanager.omcer import ndo_avail, ndo_clone, ndo_remove, ndo_build, ndo_sn301, ndo_path, ndo_get, ndo_install

def main():
    parser = ap.ArgumentParser(
        prog="ndb",
        description="Manage your OpenMC HDF5 nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # list
    avail_parser = subparsers.add_parser(
        "avail",
        help="List installed libraries"
    )
    avail_parser.set_defaults(func=ndo_avail)

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
    clone_parser.set_defaults(func=ndo_clone)

    # install
    install_parser = subparsers.add_parser(
        "install",
        help="Install one or more OpenMC libraries"
    )
    install_parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    install_parser.set_defaults(func=ndo_install)

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
    remove_parser.set_defaults(func=ndo_remove)

    # get
    get_parser = subparsers.add_parser(
        "get",
        help="Get an OpenMC nuclear data library"
    )
    get_parser.add_argument(
        "library",
        type=str,
        help="Name of the library",
    )
    get_parser.set_defaults(func=ndo_get)

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
    build_parser.set_defaults(func=ndo_build)

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
    sn301_parser.set_defaults(func=ndo_sn301)

    # path
    path_parser = subparsers.add_parser(
        "path",
        help="Get path to the library's cross_section.xml file"
    )
    path_parser.add_argument(
        "library",
        type=str,
        help="Name of the desired library"
    )
    path_parser.set_defaults(func=ndo_path)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
