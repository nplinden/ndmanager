from pathlib import Path

from ndmanager.data import ATOMIC_SYMBOL
from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import process


def process_photon(directory, photo, ard):
    import openmc.data

    data = openmc.data.IncidentPhoton.from_endf(
        photo,
        ard,
    )
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file, "w")


def generate_photon(photo_dict, ard_dict, dryrun, library):
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
