import argparse as ap

from ndmanager.API.sampling import Sampling


class NdsSampleCommand:
    """Define the `ndf sample` command"""
    def __init__(self, args: ap.Namespace) -> None:
        """Execute the `nds sample` command given an argparse namespace

        Args:
            args (ap.Namespace): An argparse namespace containing the `nds sample`
                                 arguments
        """
        self.args = args
        self.sampler = Sampling(args.filename)
        self.sampler.create_dir(args.clean)
        self.sampler.sample(args.j)

    @classmethod
    def parser(cls, subparsers):
        """Add the parser for the 'ndf sample' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "sample", help="Sample a data library given a YAML input file"
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
