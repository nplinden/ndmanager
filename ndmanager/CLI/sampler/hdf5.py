"""Definition and parser for the 'ndf hdf5' command"""

import argparse as ap
import shutil

from ndmanager.API.sampling.hdf5_sampling import HDF5Sampling


class NdsHdf5Sampling:
    """Define the `nds hdf5` command"""

    def __init__(self, args: ap.Namespace) -> None:
        """Execute the `nds pendf` command given an argparse namespace

        Args:
            args (ap.Namespace): An argparse namespace containing the `nds sample`
                                 arguments
        """
        self.args = args
        self.sampler = HDF5Sampling(args.filename, args.clean)
        shutil.copy(args.filename, self.sampler.rootpath / "input.yml")
        self.sampler.sample(1)

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction):
        """Add the parser for the 'ndf hdf5' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "hdf5", help="Sample a data library given a YAML input file"
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
