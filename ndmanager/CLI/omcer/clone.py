import argparse as ap
import shutil

from ndmanager.data import OPENMC_NUCLEAR_DATA


def clone_parser(subparsers):
    parser = subparsers.add_parser("clone", help="Clone an installed OpenMC library")
    parser.add_argument(
        "source",
        type=str,
        help="Name for the original library",
    )
    parser.add_argument(
        "target",
        type=str,
        help="Name for the new cloned library",
    )
    parser.set_defaults(func=clone)


def clone(args: ap.Namespace):
    source = OPENMC_NUCLEAR_DATA / args.source
    target = OPENMC_NUCLEAR_DATA / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)
