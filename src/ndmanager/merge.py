import h5py
from pathlib import Path


def merge_neutron_file(sourcepath: str, targetpath: str) -> None:
    """Merge two nuclear data file containing data for the same nuclide at different temperatures.

    Args:
        sourcepath: Path to the source data file. This file will not be modified
        targetpath: Path to the target data file. This file will be modified

    """
    source = h5py.File(sourcepath, "r")
    target = h5py.File(targetpath, "a")

    if len(source.keys()) != 1 or len(target.keys()) != 1:
        msg = "Both source and target files must contain data for a single nuclide"
        raise ValueError(msg)

    nuclide = next(iter(source.keys()))
    if next(iter(source.keys())) != nuclide:
        msg = "Both source and target files must contain data for the same nuclide"
        raise ValueError(msg)

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

        if "urr" in source[nuclide]:
            source.copy(source[f"{nuclide}/urr/{t}K"], target[f"{nuclide}/urr/"])


def get_available_temperature(sourcepath: Path) -> set[int]:
    with h5py.File(sourcepath, "r") as source:
        if len(source.keys()) != 1:
            msg = "The source file must contain data for a single nuclide"
            raise ValueError(msg)

        nuclide = next(iter(source.keys()))
        temperatures = source[f"{nuclide}/energy"].keys()
        return {int(t[:-1]) for t in temperatures}
