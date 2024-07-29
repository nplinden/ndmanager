import os
from pathlib import Path
import yaml
from contextlib import chdir
import openmc
import argparse as ap


if "ENDF6_PATH" in os.environ:
    endf6_path = Path(os.environ["ENDF6_PATH"])
else:
    endf6_path = None

def chain(ymlpath, destination="."):
    if endf6_path is None:
        raise EnvironmentError("The $ENDF6_PATH must be set.")

    inputs = yaml.safe_load(open(ymlpath))

    name = Path(inputs["name"])
    name.mkdir(parents=True, exist_ok=True)
    with chdir(name):
        basis = inputs["basis"]

        neutron = (endf6_path / basis / "n").glob("*.dat")
        decay = (endf6_path / basis / "decay").glob("*.dat")
        nfpy = (endf6_path / basis / "nfpy").glob("dat")

        chain = openmc.deplete.Chain.from_endf(
            neutron_files=neutron,
            decay_files=decay,
            fpy_files=nfpy,
            reactions=list(openmc.deplete.chain.REACTIONS.keys())
        )

        chain.export_to_xml(destination)

def chain_cli():
    parser = ap.ArgumentParser(
        prog="ndchain",
        description="Process ENDF6 files into OpenMC xml chain files.",
    )
    parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target library.",
    )
    parser.add_argument("destination", type=str,
                        help="Path to write the chain to.")

    args = parser.parse_args()
    chain(args.filename, args.destination)