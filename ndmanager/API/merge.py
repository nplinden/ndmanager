import h5py


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

        if "urr" in source[nuclide]:
            source.copy(source[f"{nuclide}/urr/{t}K"], target[f"{nuclide}/urr/"])
