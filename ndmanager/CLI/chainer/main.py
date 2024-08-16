import argparse as ap

from ndmanager.CLI.chainer.build import build


def main():
    parser = ap.ArgumentParser(
        prog="ndo",
        description="Manage your OpenMC HDF5 nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # build
    build_parser = subparsers.add_parser(
        "build", help="Build an OpenMC depletion chain from a YAML input file"
    )
    build_parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target depletion chain",
    )
    build_parser.set_defaults(func=build)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()