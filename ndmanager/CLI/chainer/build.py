import argparse as ap
import shutil
import yaml
from contextlib import chdir

from ndmanager.API.utils import list_endf6
from ndmanager.API.data import OPENMC_NUCLEAR_DATA


def build(args: ap.Namespace):
    import openmc.deplete

    ymlpath = args.filename
    inputs = yaml.safe_load(open(ymlpath, "r"))
    name = inputs["name"]
    hl = float(inputs.get("halflife", -1))
    f = open(ymlpath, "r")

    directory = OPENMC_NUCLEAR_DATA / "chains" / name
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    with chdir(directory):
        decay = list(list_endf6("decay", inputs["decay"]).values())
        n = list(list_endf6("n", inputs["n"]).values())
        nfpy = list(list_endf6("nfpy", inputs["nfpy"]).values())

        chain = openmc.deplete.Chain.from_endf(decay, nfpy, n)
        if hl > 0.0:
            tokeep = [
                nuc.name
                for nuc in chain.nuclides
                if nuc.half_life is None or nuc.half_life > hl
            ]
            chain = chain.reduce(tokeep)

        chain.export_to_xml(f"{name}.xml")

        with open(f"{name}.yml", "w") as target:
            print("".join(f.readlines()), file=target)
