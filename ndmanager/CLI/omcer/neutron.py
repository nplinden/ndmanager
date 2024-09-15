"""Some functions to process neutron evaluations to the OpenMC format"""

import argparse as ap
from pathlib import Path
from typing import Dict, List

import openmc.data
from openmc.data import IncidentNeutron

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import process


def _process_neutron(args):
    process_neutron(*args)


def process_neutron(
    directory: str,
    nuclide: str,
    path: str,
    temperatures: List[int],
):
    """Process a neutron evaluation to the OpenMC format for the desired
    temperatures

    Args:
        directory (str): Directory to save the file to
        nuclide (str): Name of the nuclide
        path (str): Path to the neutron evaluation tape
        temperatures (List[int]): List of integer valued temperatures
    """
    h5_file = directory / f"{nuclide}.h5"
    temp = set(temperatures)
    if h5_file.exists():
        existing = IncidentNeutron.from_hdf5(h5_file)
        existing_temperatures = set(existing.temperatures)
        temp -= existing_temperatures

    data = IncidentNeutron.from_njoy(path, temperatures=temp)
    data.export_to_hdf5(h5_file)


def generate_neutron(
    n_dict: Dict[str, str | Dict[str, str]],
    temperatures: List[int],
    library: openmc.data.DataLibrary,
    run_args: ap.Namespace,
):
    """Generate a set of neutron HDF5 data files given a dictionnary from a
    YAML library description file

    Args:
        n_dict (Dict[str, str  |  Dict[str, str]]): The dictionary from the YAML file
        temperatures (List[int]): The desired temperatures
        library (openmc.data.DataLibrary): The library object
        dryrun (bool, optional): If True, the generation won't be performed. Defaults to False.
    """
    neutron = list_endf6("n", n_dict)
    dest = Path("neutron")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, n, neutron[n], temperatures, run_args) for n in neutron]
    if run_args.dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        process(
            dest,
            library,
            _process_neutron,
            args,
            processes=run_args.j,
            key=lambda x: Nuclide.from_name(x.stem).zam,
        )
