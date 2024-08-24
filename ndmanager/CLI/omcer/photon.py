"""Some functions to process photon evaluations to the OpenMC format"""

from pathlib import Path
from typing import Dict

import openmc.data

from ndmanager.CLI.omcer.utils import process
from ndmanager.data import ATOMIC_SYMBOL
from ndmanager.utils import list_endf6


def process_photon(directory, photo, ard):
    """Process a photon evaluation to the OpenMC format

    Args:
        directory (str): Directory to save the file to
        photo (str): Path to a photo-atomic cross-section file
        ard (str): Path to an atomic relaxation data file
    """
    data = openmc.data.IncidentPhoton.from_endf(
        photo,
        ard,
    )
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file, "w")


def generate_photon(
    photo_dict: Dict[str, str | Dict[str, str]],
    ard_dict: Dict[str, str | Dict[str, str]],
    library: openmc.data.DataLibrary,
    dryrun: bool = False,
):
    """Generate a set of photon HDF5 data files given photo-atomic and atomic relaxation
    parameters from a YAML library description file

    Args:
        photo_dict (Dict[str, str  |  Dict[str, str]]): The photo-atomic parameters
        ard_dict (Dict[str, str  |  Dict[str, str]]): The atomic relaxation parameters
        library (openmc.data.DataLibrary): The library object
        dryrun (bool, optional): If True, the generation won't be performed. Defaults to False.
    """
    photo = list_endf6("photo", photo_dict)
    ard = list_endf6("ard", ard_dict)
    dest = Path("photon")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, photo[atom], ard.get(atom, None)) for atom in photo]
    if dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        process(
            dest,
            library,
            process_photon,
            args,
            "photon",
            lambda x: ATOMIC_SYMBOL[x.stem],
        )
