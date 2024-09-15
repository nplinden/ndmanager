"""Some functions to process photon evaluations to the OpenMC format"""

import argparse as ap
from pathlib import Path
from typing import Dict

import openmc.data

from ndmanager.API.endf6 import Endf6
from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import process
from ndmanager.data import ATOMIC_SYMBOL


def _process_photon(args):
    process_photon(*args)


def process_photon(directory, photo, ard):
    """Process a photon evaluation to the OpenMC format

    Args:
        directory (str): Directory to save the file to
        photo (str): Path to a photo-atomic cross-section file
        ard (str): Path to an atomic relaxation data file
    """
    h5_file = directory / f"{Endf6(photo).nuclide.element}.h5"
    if h5_file.exists():
        return
    data = openmc.data.IncidentPhoton.from_endf(
        photo,
        ard,
    )
    data.export_to_hdf5(h5_file, "w")


def generate_photon(
    photo_dict: Dict[str, str | Dict[str, str]],
    ard_dict: Dict[str, str | Dict[str, str]],
    library: openmc.data.DataLibrary,
    run_args: ap.Namespace,
):
    """Generate a set of photon HDF5 data files given photo-atomic and atomic relaxation
    parameters from a YAML library description file

    Args:
        photo_dict (Dict[str, str  |  Dict[str, str]]): The photo-atomic parameters
        ard_dict (Dict[str, str  |  Dict[str, str]]): The atomic relaxation parameters
        library (openmc.data.DataLibrary): The library object
        run_args (ap.Namespace): Arguments for the process function
    """
    photo = list_endf6("photo", photo_dict)
    ard = list_endf6("ard", ard_dict)
    dest = Path("photon")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, photo[atom], ard.get(atom, None)) for atom in photo]
    process(
        dest,
        library,
        _process_photon,
        args,
        run_args=run_args,
        key=lambda x: ATOMIC_SYMBOL[x.stem],
    )
