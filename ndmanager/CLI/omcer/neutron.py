import time
from multiprocessing import Pool
from pathlib import Path

from ndmanager.utils import list_endf6
from ndmanager.API.nuclide import Nuclide
from ndmanager.CLI.omcer.utils import process


def process_neutron(directory, path, temperatures):
    import openmc.data

    data = openmc.data.IncidentNeutron.from_njoy(path, temperatures=temperatures)
    h5_file = directory / f"{data.name}.h5"

    data.export_to_hdf5(h5_file, "w")


def generate_neutron(n_dict, temperatures, dryrun, library):
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
