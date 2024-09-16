"""Definition and parser for the `ndo build` command"""

import argparse as ap
import shutil
from contextlib import chdir

import openmc.data
import yaml

from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.CLI.omcer.neutron import generate_neutron
from ndmanager.CLI.omcer.photon import generate_photon
from ndmanager.CLI.omcer.tsl import generate_tsl
from ndmanager.data import NDMANAGER_HDF5, NDMANAGER_MODULEPATH


def build_parser(subparsers):
    """Add the parser for the 'ndo build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
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
        "--clean", help="Remove the library before building", action="store_true"
    )
    parser.add_argument("-j", type=int, default=1, help="Number of concurent processes")
    parser.set_defaults(func=build)


def build(args: ap.Namespace):
    """Build an OpenMC HDF5 nuclear data library from a YAML descriptive file

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    with open(args.filename, encoding="utf-8") as f:
        inputs = yaml.safe_load(f)
        f.seek(0)
        lines = f.readlines()

    directory = NDMANAGER_HDF5 / inputs["name"]
    if directory.exists() and args.clean:
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with chdir(directory):
        library = openmc.data.DataLibrary()

        if "n" in inputs:
            generate_neutron(inputs["n"], library, args)

        if "tsl" in inputs:
            generate_tsl(inputs["tsl"], inputs["n"], library, args)

        if "photo" in inputs:
            photo = inputs["photo"]
            ard = inputs.get("ard", None)
            generate_photon(photo, ard, library, args)

        library.export_to_xml("cross_sections.xml")
        with open(f"{inputs['name']}.yml", "w", encoding="utf-8") as target:
            print("".join(lines), file=target)

    if NDMANAGER_MODULEPATH is not None:
        name = f"xs/{inputs['name']}"
        xs_modulefile(name, inputs["description"], directory / "cross_sections.xml")
