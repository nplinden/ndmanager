"""A function that encapsulates nuclear data processing from OpenMC"""

import argparse as ap
import multiprocessing as mp
import time
from pathlib import Path
from typing import Callable, Tuple

import h5py
import openmc.data
from tqdm import tqdm


def process(
    dest: Path,
    library: openmc.data.DataLibrary,
    processor: Callable,
    args: Tuple,
    run_args: ap.Namespace,
    key: Callable = lambda x: x,
):
    """Encapsulation fo the nuclear data processing capabilities of OpenMC

    Args:
        dest (Path): The directory to write the files to
        library (openmc.data.DataLibrary): The library object
        processor (function): The function use to process the data
        args (Tuple): The list of arguments to pass to the processor
        key (_type_, optional): The sort key for the cross_sections.xml file. Defaults to lambdax:x.
    """
    if "neutron" in processor.__name__:
        desc = "Neutron"
    elif "tsl" in processor.__name__:
        desc = "TSL    "
    elif "photon" in processor.__name__:
        desc = "Photon "
    else:
        desc = "       "

    if run_args.dryrun:
        for arg in args:
            print(arg[0], str(arg[1]), str(arg[2]))
    else:
        with mp.get_context("spawn").Pool(processes=run_args.j) as p:
            bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
            pbar = tqdm(total=len(args), bar_format=bar_format, desc=desc)

            def update_pbar(_):
                pbar.update()

            for arg in args:
                p.apply_async(processor, args=(arg,), callback=update_pbar)

            p.close()
            p.join()
            pbar.close()

    for path in sorted(dest.glob("*.h5"), key=key):
        library.register_file(path)


def merge_neutron_file(sourcepath, targetpath):
    """Merge two nuclear data file containing data for the same nuclide at
    different temperatures.

    Args:
        sourcepath: Path to the source data file. This file will not be modified
        targetpath: Path to the target data file. This file will be modified
    """
    source = h5py.File(sourcepath, "r")
    target = h5py.File(targetpath, "a")

    assert len(source.keys()) == 1
    assert len(target.keys()) == 1
    nuclide = list(source.keys())[0]
    assert list(source.keys())[0] == nuclide

    s_temperatures = source[f"{nuclide}/energy"].keys()
    s_temperatures = {int(t[:-1]) for t in s_temperatures}
    t_temperatures = target[f"{nuclide}/energy"].keys()
    t_temperatures = {int(t[:-1]) for t in t_temperatures}

    new_temperatures = s_temperatures - t_temperatures

    for t in new_temperatures:
        source.copy(source[f"{nuclide}/energy/{t}K"], target[f"{nuclide}/energy/"])
        source.copy(source[f"{nuclide}/kTs/{t}K"], target[f"{nuclide}/kTs/"])

        for reaction in source[f"{nuclide}/reactions"]:
            source.copy(
                source[f"{nuclide}/reactions/{reaction}/{t}K"],
                target[f"{nuclide}/reactions/{reaction}/"],
            )


def get_temperatures(inputs):
    """Turns YAML temperature field to a list of interger temperatures

    Args:
        inputs (Dict[str, int | float | str]): YAML temperature field

    Returns:
        List[int]: The list of integer temperatures
    """
    temperatures = inputs.get("temperatures", 293)
    if isinstance(temperatures, (int, float)):
        temperatures = [int(temperatures)]
    else:
        temperatures = [int(t) for t in temperatures.split()]
    return temperatures
