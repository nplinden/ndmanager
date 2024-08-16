from pathlib import Path

from ndmanager.API.data import ENDF6_PATH, TSL_NEUTRON
from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import process


def process_tsl(directory, neutron, thermal):
    import openmc.data

    data = openmc.data.ThermalScattering.from_njoy(neutron, thermal)
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file)


def list_tsl(tsl_params, neutrons):
    basis = tsl_params["basis"]
    sub = tsl_params.get("substitute", {})
    ommit = tsl_params.get("ommit", "").split()
    add = tsl_params.get("add", {})

    basis_neutrons = TSL_NEUTRON[basis]
    basis_paths = (ENDF6_PATH / basis / "tsl").glob("*.dat")
    basis_paths = [p for p in basis_paths if p.name not in ommit]

    couples = []
    for t in basis_paths:
        nuclide = basis_neutrons[t.name]
        nuclide = neutrons[sub.get(nuclide, nuclide)]
        couples.append((nuclide, t))

    for guestlib, _tsl in add.items():
        tsl = _tsl.split()
        for t in tsl:
            gpath = ENDF6_PATH / guestlib / "tsl" / t
            nuclide = TSL_NEUTRON[guestlib][t]
            nuclide = neutrons[sub.get(nuclide, nuclide)]
            couples.append((nuclide, gpath))

    return couples


def generate_tsl(tsl_params, neutron_params, temperatures, dryrun, library):
    neutrons = list_endf6("n", neutron_params)
    tsl = list_tsl(tsl_params, neutrons)

    dest = Path("tsl")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, n, t) for n, t in tsl]
    if dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        process(
            dest,
            library,
            process_tsl,
            args,
            "TSL",
        )
