from h5py import File
import os
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
from ndmanager import OPENMC_NUCLEAR_DATA


def overwrite(nuclide, mt, sourcefile, targetfile):
    with File(sourcefile, "r") as source, File(targetfile, "r+") as target:

        source_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]
        target_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]

        source_temperatures = [int(T[:-1]) for T in source_rgroup.keys() if "K" in T]
        target_temperatures = [int(T[:-1]) for T in target_rgroup.keys() if "K" in T]
        temperatures = target_temperatures

        for T in temperatures:
            if T not in source_temperatures:
                raise ValueError(
                    f"Temperature {T} not available for MT={mt} in {sourcefile}"
                )

        for T in temperatures:
            target_grid = target[f"{nuclide}/energy/{T:d}K"][...]
            target_attrs = target[
                f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"
            ].attrs

            source_grid = source[f"{nuclide}/energy/{T:d}K"][...]
            source_xs = source[f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"][...]

            replacement = np.interp(target_grid, source_grid, source_xs)
            del target[f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"]
            target[f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"] = replacement
            for k, v in target_attrs.items():
                target[f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"].attrs[k] = v


def find_negative(libpath, mt):
    result = {}
    with File(libpath, "r") as f:
        nuclides = list(f.keys())
        for nuclide in nuclides:
            try:
                rgroup = f[f"{nuclide}/reactions/reaction_{mt:03d}/"]
            except KeyError:
                continue
            temperatures = [T for T in rgroup.keys() if "K" in T]
            negatives = []
            for T in temperatures:
                xs = f[f"{nuclide}/reactions/reaction_{mt:03d}/{T}/xs"][...]
                if np.any(xs < 0):
                    negatives.append(T)
            if negatives:
                result[nuclide] = {"path": libpath, "temperatures": negatives}
    if result:
        return result
    else:
        return {}


def find_negative_in_lib(libfile, mt):
    plib = Path(libfile)
    root = ET.parse(plib).getroot()

    directorynode = root.find("directory")
    if directorynode is not None:
        directory = directorynode.text
    else:
        directory = ""

    negatives = {}
    for lib in root.findall("library"):
        if lib.attrib.get("type") == "neutron":
            libpath = plib.parent / directory / lib.attrib["path"]
            negatives |= find_negative(libpath, mt)
    return negatives


def set_negative_to_zero(file, nuclide, mt):
    with File(file, "r+") as f:
        try:
            rgroup = f[f"{nuclide}/reactions/reaction_{mt:03d}/"]
        except KeyError:
            return
        temperatures = [T for T in rgroup.keys() if "K" in T]
        for T in temperatures:
            xs = f[f"{nuclide}/reactions/reaction_{mt:03d}/{T}/xs"][...]
            f[f"{nuclide}/reactions/reaction_{mt:03d}/{T}/xs"][xs < 0] = 0.0
    return


def set_negative_to_zero_in_lib(libfile, mt):
    plib = Path(libfile)
    root = ET.parse(plib).getroot()

    directorynode = root.find("directory")
    if directorynode is not None:
        directory = directorynode.text
    else:
        directory = ""

    for lib in root.findall("library"):
        if lib.attrib.get("type") == "neutron":
            libpath = plib.parent / directory / lib.attrib["path"]
            set_negative_to_zero(libpath, lib.attrib["materials"], mt)
    return


def find_nuclide_in_lib(libfile, nuclide):
    plib = Path(libfile)
    root = ET.parse(plib).getroot()

    directorynode = root.find("directory")
    if directorynode is not None:
        directory = directorynode.text
    else:
        directory = ""

    for lib in root.findall("library"):
        if lib.attrib.get("type") == "neutron" and lib.attrib["materials"] == nuclide:
            return plib.parent / directory / lib.attrib["path"]
