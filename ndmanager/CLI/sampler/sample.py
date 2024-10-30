import argparse as ap

from ndmanager.API.sampling import Sampling


class NdsSampleCommand:
    def __init__(self, args: ap.Namespace) -> None:
        self.args = args
        self.sampler = Sampling(args.filename)
        self.sampler.create_dir(args.clean)
        self.sampler.sample(args.j)

    @classmethod
    def parser(cls, subparsers):
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
