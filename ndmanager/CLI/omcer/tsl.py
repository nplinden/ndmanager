"""Some functions to process Thermal Scattering Law evaluations to the OpenMC format"""

import argparse as ap
from pathlib import Path
from typing import Dict, List

import openmc.data

from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import get_temperatures, process
from ndmanager.data import NDMANAGER_ENDF6, TSL_NEUTRON


def _process_tsl(args):
    process_tsl(*args)


def process_tsl(directory: str, neutron: str, thermal: str, temperatures: List[int]):
    """Process a TSL evaluations given a companion neutron evaluation

    Args:
        directory (str): Directory to save the file to
        neutron (str): Path to a neutron evaluation tape
        thermal (str): Path to a tsl evaluation tape
    """
    data = openmc.data.ThermalScattering.from_njoy(neutron, thermal, temperatures)
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file, "w")


def get_temperatures(tapename, tsl_params):
    node = tsl_params.get("temperatures", {})
    if tapename not in node:
        return None
    if isinstance(node[tapename], str):
        return [int(i) for i in node[tapename].split()]
    return [node[tapename]]


def list_tsl(tsl_params: Dict[str, str], neutrons: Dict[str, Path]):
    """List the paths to ENDF6 tsl evaluations necessary to build the cross sections

    Args:
        tsl_params (Dict[str, str]): The parameters in the form of a dictionnary
        neutrons (Dict[str, Path]): The list of the necessary neutron evaluation tapes

    Returns:
        Dict[str, Path]: A dictionnary that associates nuclide names to couples of ENDF6 paths
    """
    basis = tsl_params["basis"]
    sub = tsl_params.get("substitute", {})
    ommit = tsl_params.get("ommit", "").split()

    basis_neutrons = TSL_NEUTRON[basis]
    basis_paths = (NDMANAGER_ENDF6 / basis / "tsl").glob("*.endf6")
    basis_paths = [p for p in basis_paths if p.name not in ommit]

    couples = []
    for tsl in basis_paths:
        nuclide = basis_neutrons[tsl.name]
        if nuclide in sub:
            nuclide = sub[nuclide]
        temperatures = get_temperatures(tsl.name, tsl_params)
        couples.append((neutrons[nuclide], tsl, temperatures))

    for guestlib, _tsl in tsl_params.get("add", {}).items():
        tsl = _tsl.split()
        for t in tsl:
            temperatures = get_temperatures(t, tsl_params)
            gpath = NDMANAGER_ENDF6 / guestlib / "tsl" / t
            nuclide = TSL_NEUTRON[guestlib][t]
            nuclide = neutrons[sub.get(nuclide, nuclide)]
            couples.append((nuclide, gpath, temperatures))

    return couples


def generate_tsl(
    tsl_params: Dict[str, str],
    neutron_params: Dict[str, str],
    library: openmc.data.DataLibrary,
    run_args: ap.Namespace,
):
    """Generate a set of tsl HDF5 data files given tsl and neutron dictionnaries from a
    YAML library description file

    Args:
        tsl_params (Dict[str, str]): The tsl dictionnary from the YAML file
        neutron_params (Dict[str, str]): The neutron dictionnary from the YAML file
        library (openmc.data.DataLibrary): The library object
        run_args (ap.Namespace): Arguments for the process function
    """
    neutrons = list_endf6("n", neutron_params)
    tsls = list_tsl(tsl_params, neutrons)

    dest = Path("tsl")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, n, tsl, t) for n, tsl, t in tsls]
    process(
        dest,
        library,
        _process_tsl,
        args,
        run_args=run_args,
    )
