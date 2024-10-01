"""Some functions to process neutron evaluations to the OpenMC format"""

import argparse as ap
from pathlib import Path
from typing import Dict, List
from loguru import logger
import warnings
import time

import openmc.data
from openmc.data import IncidentNeutron

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import list_endf6
from ndmanager.CLI.omcer.utils import (get_temperatures, merge_neutron_file,
                                       process)


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
    loggerpath = directory / "logs" / f"{nuclide}.log"
    logger.remove()
    format = "{time:DD-MMM-YYYY HH:mm:ss}" "| {level:<8}" "| {message}"
    logger.add(loggerpath, format=format, level="INFO")

    def showwarning(message, *args, **kwargs):
        logger.warning(message)

    warnings.showwarning = showwarning

    targetpath = directory / f"{nuclide}.h5"
    temp = set(temperatures)
    logger.info("PROCESS NEUTRON DATA")
    logger.info(f"Nuclide: {nuclide}")
    logger.info(f"Temperatures: {temp}")
    t0 = time.time()
    if targetpath.exists():
        logger.info(f"Processed file already exists at {targetpath}")
        target = IncidentNeutron.from_hdf5(targetpath)
        target_temp = {int(t[:-1]) for t in target.temperatures}
        logger.info(f"Existing temperatures: {target_temp}")

        temp -= target_temp
        if not temp:
            logger.info("No new processing is necessary, exiting")
            return
        logger.info(f"New processing temperatures: {temp}")
        sourcepath = directory / f"tmp_{nuclide}.h5"
        source = IncidentNeutron.from_njoy(path, temperatures=temp)
        source.export_to_hdf5(sourcepath, "w")
        merge_neutron_file(sourcepath, targetpath)
        sourcepath.unlink()
    else:
        data = IncidentNeutron.from_njoy(path, temperatures=temp)
        data.export_to_hdf5(targetpath, "w")
    logger.info(f"Processing time: {time.time() - t0:.1f}")


def generate_neutron(
    n_dict: Dict[str, str | Dict[str, str]],
    library: openmc.data.DataLibrary,
    run_args: ap.Namespace,
):
    """Generate a set of neutron HDF5 data files given a dictionnary from a
    YAML library description file

    Args:
        n_dict (Dict[str, str  |  Dict[str, str]]): The dictionary from the YAML file
        temperatures (List[int]): The desired temperatures
        library (openmc.data.DataLibrary): The library object
        run_args (ap.Namespace): Arguments for the process function
    """
    neutron = list_endf6("n", n_dict)
    temperatures = get_temperatures(n_dict)
    dest = Path("neutron")
    dest.mkdir(parents=True, exist_ok=True)
    args = [(dest, n, neutron[n], temperatures) for n in neutron]
    process(
        dest,
        library,
        _process_neutron,
        args,
        run_args=run_args,
        key=lambda x: Nuclide.from_name(x.stem).zam,
    )
