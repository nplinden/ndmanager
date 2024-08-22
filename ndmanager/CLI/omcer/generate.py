from contextlib import chdir
import shutil

import yaml

from ndmanager.data import ENDF6_PATH, OPENMC_NUCLEAR_DATA, NDMANAGER_MODULEPATH
from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.CLI.omcer.neutron import generate_neutron
from ndmanager.CLI.omcer.photon import generate_photon
from ndmanager.CLI.omcer.tsl import generate_tsl


def get_temperatures(inputs):
    temperatures = inputs.get("temperatures", 293)
    if isinstance(temperatures, int) or isinstance(temperatures, float):
        temperatures = [int(temperatures)]
    else:
        temperatures = [int(t) for t in temperatures.split()]
    return temperatures


def generate(ymlpath, dryrun=False):
    import openmc.data

    inputs = yaml.safe_load(open(ymlpath))
    f = open(ymlpath, "r")

    directory = OPENMC_NUCLEAR_DATA / "custom" / inputs["name"]
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    with chdir(directory):
        library = openmc.data.DataLibrary()
        temperatures = get_temperatures(inputs)

        if "n" in inputs:
            generate_neutron(inputs["n"], temperatures, dryrun, library)

        if "tsl" in inputs:
            generate_tsl(inputs["tsl"], inputs["n"], temperatures, dryrun, library)

        if "photo" in inputs:
            photo = inputs["photo"]
            ard = inputs.get("ard", None)
            generate_photon(photo, ard, dryrun, library)

        library.export_to_xml("cross_sections.xml")
        with open(f"{inputs['name']}.yml", "w") as target:
            print("".join(f.readlines()), file=target)

    if NDMANAGER_MODULEPATH is not None:
        name = f"xs/{inputs['name']}"
        xs_modulefile(name, inputs["description"], directory / "cross_sections.xml")


def chain(ymlpath):
    import openmc.deplete

    inputs = yaml.safe_load(open(ymlpath))

    name = OPENMC_NUCLEAR_DATA / inputs["name"]
    name.mkdir(parents=True, exist_ok=True)
    with chdir(name):
        basis = inputs["basis"]

        neutron = (ENDF6_PATH / basis / "n").glob("*.dat")
        decay = (ENDF6_PATH / basis / "decay").glob("*.dat")
        nfpy = (ENDF6_PATH / basis / "nfpy").glob("dat")

        chainfile = openmc.deplete.Chain.from_endf(
            neutron_files=neutron,
            decay_files=decay,
            fpy_files=nfpy,
            reactions=list(openmc.deplete.chain.REACTIONS.keys()),
            progress=False,
        )

        chainfile.export_to_xml("chain.xml")
