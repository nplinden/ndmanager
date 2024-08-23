"""Some functions to process neutron evaluations to the OpenMC format"""
from pathlib import Path
from typing import Dict, List

import openmc.data

from ndmanager.API.nuclide import Nuclide
from ndmanager.CLI.omcer.utils import process
from ndmanager.utils import list_endf6


def process_neutron(directory: str, path: str, temperatures: List[int]):
    """Process a neutron evaluation to the OpenMC format for the desired
    temperatures

    Args:
        directory (str): Directory to save the file to
        path (str): Path to the neutron evaluation tape
        temperatures (List[int]): List of integer valued temperatures
    """

    data = openmc.data.IncidentNeutron.from_njoy(path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    data.export_to_hdf5(h5_file, "w")


def generate_neutron(
    n_dict: Dict[str, str | Dict[str, str]],
    temperatures: List[int],
    library: openmc.data.DataLibrary,
    dryrun: bool = False,
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
    args = [(dest, neutron[n], temperatures) for n in neutron]
    if dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        process(
            dest,
            library,
            process_neutron,
            args,
            "neutron",
            lambda x: Nuclide.from_name(x.stem).zam,
        )
