"""Definition and parser for the 'ndf pendf' command"""

import argparse as ap
import shutil

from ndmanager.API.sampling.pendf_sampling import PendfSampling


class NdsPendfCommand:
    """Define the `nds pendf` command"""

    def __init__(self, args: ap.Namespace) -> None:
        """Execute the `nds pendf` command given an argparse namespace

        Args:
            args (ap.Namespace): An argparse namespace containing the `nds sample`
                                 arguments
        """
        self.args = args
        self.sampler = PendfSampling(args.filename, args.clean)
        shutil.copy(args.filename, self.sampler.rootpath / "input.yml")
        self.sampler.sample(args.j)

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction):
        """Add the parser for the 'ndf pendf' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "pendf", help="Sample a data library given a YAML input file"
        )
        parser.add_argument(
            "filename",
            type=str,
            help="The name of the YAML file describing the target library",
        )
        parser.add_argument(
            "--clean",
            "-c",
            action="store_true",
            help="Wether to delete the sample directory if it already exists",
        )
        parser.add_argument(
            "-j", type=int, default=1, help="Number of concurent processes"
        )
        parser.set_defaults(func=cls)
