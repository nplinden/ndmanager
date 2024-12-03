"""Definition and parser for the `ndo build` command"""

import argparse as ap
import shutil

import yaml

from ndmanager import __version__
from ndmanager.API.process.ndm_library import NDMLibrary
from ndmanager.CLI.parser import Command


class NdoBuildCommand(Command):
    """define the `ndo build` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndo build' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "build", help="Build an OpenMC library from a YAML input file"
        )
        parser.add_argument(
            "filename",
            type=str,
            help="The name of the YAML file describing the target library",
        )
        parser.add_argument(
            "--dryrun", help="Do not perform NJOY runs", action="store_true"
        )
        parser.add_argument(
            "--clean", help="Remove the library before building", action="store_true"
        )
        parser.add_argument(
            "--temperatures",
            "-T",
            help="Override the temperature values in the input file",
            nargs="+",
            type=int,
            default=None,
        )
        parser.add_argument(
            "-j", type=int, default=1, help="Number of concurent processes"
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """Build an OpenMC HDF5 nuclear data library from a YAML descriptive file

        Args:
            args (ap.Namespace): The argparse object containing the command line argument
        """

        with open(args.filename, encoding="utf-8") as f:
            inputs = yaml.safe_load(f)

        header = f"NDManager {__version__}"
        print(header)
        print("".join(["-" for _ in header]))
        print(f"Building '{inputs['name']}' library")
        if "summary" in inputs:
            print(f"Summary: {inputs['summary']}")
        if args.temperatures is not None:
            print(f"Overriding input file temperatures with: {args.temperatures}")
        print()

        lib = NDMLibrary(args.filename)
        if args.temperatures is not None:
            lib.neutron.update_temperatures(set(args.temperatures))
            print(f"Custom temperatures: {args.temperatures}")
        lib.process(args.j, args.dryrun, args.clean)
        shutil.copy(args.filename, lib.root / "input.yml")
