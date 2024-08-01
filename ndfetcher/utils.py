from h5py import File
import os
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
from ndfetcher import OMC_LIBRARIES


def overwrite(nuclide, mt, sourcefile, targetfile):
    with File(sourcefile, "r") as source, File(targetfile, "r+") as target:

        source_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]
        target_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]

        source_temperatures = [int(T[:-1]) for T in source_rgroup.keys() if "K" in T]
        target_temperatures = [int(T[:-1]) for T in target_rgroup.keys() if "K" in T]
        temperatures = target_temperatures

        for T in temperatures:
            if T not in source_temperatures:
                raise ValueError(f"Temperature {T} not available for MT={mt} in {sourcefile}")

        for T in temperatures:
            target_grid = target[f"{nuclide}/energy/{T:d}K"][...]
            target_attrs = target[f"{nuclide}/reactions/reaction_{mt:03d}/{T}K/xs"].attrs

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
            f[f"{nuclide}/reactions/reaction_{mt:03d}/{T}/xs"][xs < 0] = 0.
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


def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)


def print_offset(s, offset, offsetstart):
    col, _ = os.get_terminal_size()
    indices = list(range(0, len(s), col - offset))
    parts = [s[i:j] for i, j in zip(indices, indices[1:] + [None])]
    for i in range(len(parts)):
        if i >= offsetstart:
            parts[i] = (offset * " ") + parts[i]
    print("\n".join(parts))

def set_ndl(libname):
    import openmc

    if libname[-4:] == ".xml":
        openmc.config["cross_sections"] = libname
    else:
        p = OMC_LIBRARIES / libname / "cross_sections.xml"
        if p.exists():
            openmc.config["cross_sections"] = p
        else:
            raise FileNotFoundError(f"Invalid library name '{libname}'")

def set_chain(libname):
    import openmc 

    if libname[-4:] == ".xml":
        openmc.config["chain_file"] = libname
    else:
        p = OMC_LIBRARIES / libname
        if not p.exists():
            raise FileNotFoundError(f"Invalid library name '{libname}'")
        p = p / "chain.xml"
        if  not p.exists():
            raise FileNotFoundError(f"No chain available for library '{libname}'")
        openmc.config["chain_file"] = p 

def set_nuclear_data(libname, chain=False):
    set_ndl(libname)
    if chain:
        set_chain(libname)