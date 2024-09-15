"""Some functions to process Thermal Scattering Law evaluations to the OpenMC format"""

import argparse as ap
from pathlib import Path
from typing import Dict

import openmc.data

from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import process
from ndmanager.data import NDMANAGER_ENDF6, TSL_NEUTRON


def _process_tsl(args):
    process_tsl(*args)


def process_tsl(directory: str, neutron: str, thermal: str, run_args: ap.Namespace):
    """Process a TSL evaluations given a companion neutron evaluation

    Args:
        directory (str): Directory to save the file to
        neutron (str): Path to a neutron evaluation tape
        thermal (str): Path to a tsl evaluation tape
    """

    data = openmc.data.ThermalScattering.from_njoy(neutron, thermal)
    h5_file = directory / f"{data.name}.h5"
    data.export_to_hdf5(h5_file)


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
    add = tsl_params.get("add", {})

    basis_neutrons = TSL_NEUTRON[basis]
    basis_paths = (NDMANAGER_ENDF6 / basis / "tsl").glob("*.endf6")
    basis_paths = [p for p in basis_paths if p.name not in ommit]

    couples = []
    for t in basis_paths:
        nuclide = basis_neutrons[t.name]
        if nuclide in sub:
            nuclide = sub[nuclide]
        couples.append((neutrons[nuclide], t))

    for guestlib, _tsl in add.items():
        tsl = _tsl.split()
        for t in tsl:
            gpath = NDMANAGER_ENDF6 / guestlib / "tsl" / t
            nuclide = TSL_NEUTRON[guestlib][t]
            nuclide = neutrons[sub.get(nuclide, nuclide)]
            couples.append((nuclide, gpath))

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
        dryrun (bool, optional): If True, the generation won't be performed. Defaults to False.
    """
    neutrons = list_endf6("n", neutron_params)
    tsl = list_tsl(tsl_params, neutrons)

    dest = Path("tsl")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, n, t, run_args) for n, t in tsl]
    if run_args.dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        process(
            dest,
            library,
            _process_tsl,
            args,
            "TSL",
            run_args.j,
        )
