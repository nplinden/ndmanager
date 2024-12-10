"""Definition and parser for the `ndc build` command"""

import argparse as ap

from openmc.deplete.chain import Chain
import yaml

from ndmanager.API.endf6 import list_endf6
from ndmanager.CLI.chainer.branching_ratios import branching_ratios
from ndmanager.env import NDMANAGER_CHAINS
from ndmanager.CLI.parser import Command

REACTIONS = [
    "(n,2nd)",
    "(n,2n)",
    "(n,3n)",
    "(n,na)",
    "(n,n3a)",
    "(n,2na)",
    "(n,3na)",
    "(n,np)",
    "(n,n2a)",
    "(n,2n2a)",
    "(n,nd)",
    "(n,nt)",
    "(n,n3He)",
    "(n,nd2a)",
    "(n,nt2a)",
    "(n,4n)",
    "(n,2np)",
    "(n,3np)",
    "(n,n2p)",
    "(n,npa)",
    "(n,gamma)",
    "(n,p)",
    "(n,d)",
    "(n,t)",
    "(n,3He)",
    "(n,a)",
    "(n,2a)",
    "(n,3a)",
    "(n,2p)",
    "(n,pa)",
    "(n,t2a)",
    "(n,d2a)",
    "(n,pd)",
    "(n,pt)",
    "(n,da)",
    "(n,5n)",
    "(n,6n)",
    "(n,2nt)",
    "(n,ta)",
    "(n,4np)",
    "(n,3nd)",
    "(n,nda)",
    "(n,2npa)",
    "(n,7n)",
    "(n,8n)",
    "(n,5np)",
    "(n,6np)",
    "(n,7np)",
    "(n,4na)",
    "(n,5na)",
    "(n,6na)",
    "(n,7na)",
    "(n,4nd)",
    "(n,5nd)",
    "(n,6nd)",
    "(n,3nt)",
    "(n,4nt)",
    "(n,5nt)",
    "(n,6nt)",
    "(n,2n3He)",
    "(n,3n3He)",
    "(n,4n3He)",
    "(n,3n2p)",
    "(n,3n2a)",
    "(n,3npa)",
    "(n,dt)",
    "(n,npd)",
    "(n,npt)",
    "(n,ndt)",
    "(n,np3He)",
    "(n,nd3He)",
    "(n,nt3He)",
    "(n,nta)",
    "(n,2n2p)",
    "(n,p3He)",
    "(n,d3He)",
    "(n,3Hea)",
    "(n,4n2p)",
    "(n,4n2a)",
    "(n,4npa)",
    "(n,3p)",
    "(n,n3p)",
    "(n,3n2pa)",
    "(n,5n2p)",
]


class NdcBuildCommand(Command):
    """Define the `ndc build` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
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
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """Build an OpenMC depletion chain from a YAML descriptive file

        Args:
            args (ap.Namespace): The argparse object containing the command line argument
        """

        with open(args.filename, encoding="utf-8") as f:
            inputs = yaml.safe_load(f)
        name = inputs["name"]
        hl = float(inputs.get("halflife", -1))

        target = NDMANAGER_CHAINS / f"{name}.xml"
        if target.exists():
            raise FileExistsError("A chain with that name already exists")

        decay = list(list_endf6("decay", inputs["decay"]).values())
        n = list(list_endf6("n", inputs["n"]).values())
        nfpy = list(list_endf6("nfpy", inputs["nfpy"]).values())

        chain = Chain.from_endf(decay, nfpy, n, REACTIONS)
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
