"""Definition and parser for the `ndc build` command"""

import argparse as ap
import shutil
from contextlib import chdir

import openmc.deplete
import yaml

from ndmanager.API.utils import list_endf6
from ndmanager.CLI.chainer.branching_ratios import branching_ratios
from ndmanager.CLI.chainer.module import chain_modulefile
from ndmanager.data import NDMANAGER_CHAINS, NDMANAGER_MODULEPATH


def build_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndc build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "build", help="Build an OpenMC depletion chain from a YAML input file"
    )
    parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target depletion chain",
    )
    parser.set_defaults(func=build)


def build(args: ap.Namespace):
    """Build an OpenMC depletion chain from a YAML descriptive file

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """

    with open(args.filename, encoding="utf-8") as f:
        inputs = yaml.safe_load(f)
        f.seek(0)
    name = inputs["name"]
    hl = float(inputs.get("halflife", -1))

    target = NDMANAGER_CHAINS / name
    directory = target.parent
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    with chdir(directory):
        decay = list(list_endf6("decay", inputs["decay"]).values())
        n = list(list_endf6("n", inputs["n"]).values())
        nfpy = list(list_endf6("nfpy", inputs["nfpy"]).values())

        reactions = list(openmc.deplete.chain.REACTIONS.keys())
        chain = openmc.deplete.Chain.from_endf(decay, nfpy, n, reactions)
        if hl > 0.0:
            tokeep = [
                nuc.name
                for nuc in chain.nuclides
                if nuc.half_life is None or nuc.half_life > hl
            ]
            chain = chain.reduce(tokeep)

        if "branching_ratios" in inputs:
            ratios = branching_ratios[inputs["branching_ratios"]]
            for reaction, br in ratios.items():
                chain.set_branch_ratios(
                    branch_ratios=br, reaction=reaction, strict=False
                )

    chain.export_to_xml(target)

    if NDMANAGER_MODULEPATH is not None:
        description = inputs.get("description", "")
        chain_modulefile(name, description, NDMANAGER_CHAINS / name)
