import time
from contextlib import chdir
from pathlib import Path

import yaml

from ndmanager.API.data import ENDF6_PATH, OPENMC_NUCLEAR_DATA, TSL_NEUTRON
from ndmanager.API.nuclide import Nuclide

from ndmanager.CLI.omcer.neutron import generate_neutron
from ndmanager.CLI.omcer.tsl import generate_tsl
from ndmanager.CLI.omcer.utils import process
from ndmanager.API.data import ATOMIC_SYMBOL


def process_photon(directory, photo, ard):
    import openmc.data

    data = openmc.data.IncidentPhoton.from_endf(
        photo,
        ard,
    )
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file, "w")


def list_photo(photon_params):
    basis = photon_params["basis"]
    ommit = photon_params.get("ommit", "").split()
    add = photon_params.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = (ENDF6_PATH / basis / "photo").glob("*.endf6")
    basis_dict = {p.stem: p for p in basis_paths}

    for photo in ommit:
        basis_dict.pop(photo, None)

    for guestlib, _photo in add.items():
        photo = _photo.split()
        guest_paths = (ENDF6_PATH / guestlib / "photo").glob("*.endf6")
        guest_dict = {p.stem: p for p in guest_paths if p.stem in photo}
        basis_dict |= guest_dict

    return basis_dict


def list_ard(arg_params):
    basis = arg_params["basis"]
    ommit = arg_params.get("ommit", "").split()
    add = arg_params.get("add", {})

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = (ENDF6_PATH / basis / "ard").glob("*.endf6")
    basis_dict = {p.stem: p for p in basis_paths}

    # Remove unwanted evaluations
    for ard in ommit:
        basis_dict.pop(ard, None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    for guestlib, _ard in add.items():
        ard = _ard.split()
        guest_paths = (ENDF6_PATH / guestlib / "ard").glob("*.endf6")
        guest_dict = {p.stem: p for p in guest_paths if p.stem in ard}
        basis_dict |= guest_dict

    return basis_dict


def generate_photon(photo_dict, ard_dict, dryrun, library):
    photo = list_photo(photo_dict)
    ard = list_ard(ard_dict)
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
