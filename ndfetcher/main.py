import os
from pathlib import Path
import argparse as ap
from ndfetcher.data import NSUB, NDLIBS
from ndfetcher.download import download_cmd
from ndfetcher.generate import generate_cmd

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
                                choices=list(NDLIBS.keys()),
                                help="List of nuclear data libraries to download."
                                )
    download_parser.add_argument("-s", 
                                "--sub",
                                action="extend",
                                nargs="+",
                                type=str,
                                choices=NSUB,
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
    build_parser.set_defaults(func=generate_cmd)


    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

# if __name__=="__main__":
#     main()