import argparse as ap
import shutil
from contextlib import chdir
import openmc.data

import yaml
from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.CLI.omcer.neutron import generate_neutron
from ndmanager.CLI.omcer.photon import generate_photon
from ndmanager.CLI.omcer.tsl import generate_tsl
from ndmanager.data import ENDF6_PATH, NDMANAGER_MODULEPATH, OPENMC_NUCLEAR_DATA


def get_temperatures(inputs):
    temperatures = inputs.get("temperatures", 293)
    if isinstance(temperatures, int) or isinstance(temperatures, float):
        temperatures = [int(temperatures)]
    else:
        temperatures = [int(t) for t in temperatures.split()]
    return temperatures


def build_parser(subparsers):
    parser = subparsers.add_parser(
        "build", help="Build an OpenMC library from a YAML input file"
    )
    parser.add_argument(
        "filename",
        type=str,
        help="The name of the YAML file describing the target library",
    )
    parser.add_argument(
        "--dryrun", help="Do not perform NJOY runs", action="store_true"
    )
    parser.add_argument(
        "--chain", help="Builds the depletion chain", action="store_true"
    )
    parser.set_defaults(func=build)


def build(args: ap.Namespace):

    inputs = yaml.safe_load(open(args.filename))
    f = open(args.filename, "r")

    directory = OPENMC_NUCLEAR_DATA / inputs["name"]
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    with chdir(directory):
        library = openmc.data.DataLibrary()
        temperatures = get_temperatures(inputs)

        if "n" in inputs:
            generate_neutron(inputs["n"], temperatures, args.dryrun, library)

        if "tsl" in inputs:
            generate_tsl(inputs["tsl"], inputs["n"], temperatures, args.dryrun, library)

        if "photo" in inputs:
            photo = inputs["photo"]
            ard = inputs.get("ard", None)
            generate_photon(photo, ard, args.dryrun, library)

        library.export_to_xml("cross_sections.xml")
        with open(f"{inputs['name']}.yml", "w") as target:
            print("".join(f.readlines()), file=target)

    if NDMANAGER_MODULEPATH is not None:
        name = f"xs/{inputs['name']}"
        xs_modulefile(name, inputs["description"], directory / "cross_sections.xml")
