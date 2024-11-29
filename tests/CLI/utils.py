import shlex

from ndmanager.CLI.fetcher.main import parser as ndf_parser
from ndmanager.CLI.omcer.main import parser as ndo_parser
from ndmanager.CLI.chainer.main import parser as ndc_parser
from ndmanager.CLI.sampler.main import parser as nds_parser

def nd_(parser):
    def func(command):
        args = parser.parse_args(shlex.split(command))
        args.func(args)
    return func

ndf = nd_(ndf_parser)
ndo = nd_(ndo_parser)
ndc = nd_(ndc_parser)
nds = nd_(nds_parser)