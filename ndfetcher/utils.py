from h5py import File
import os
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path

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
    

def replace_negatives_in_lib(targetlib, sources, mt, dryrun=False, verbose=True):
    negatives = find_negative_in_lib(targetlib, mt)
    source_negatives = {source: find_negative_in_lib(source, mt) for source in sources}

    for nuclide in negatives:
        found = False
        for sourcelib, sn in source_negatives.items():
            source = find_nuclide_in_lib(sourcelib, nuclide)
            target = find_nuclide_in_lib(targetlib, nuclide)
            if source is None:
                continue
            elif nuclide in sn:
                continue
            else:
                found = True
                if verbose:
                    print(f"Replacing\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}")
                if not dryrun:
                    overwrite(nuclide, mt, source, target)
                continue
        if not found:
            if verbose:
                print(f"No replacement found\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}")
            if not dryrun:
                set_negative_to_zero(target, nuclide, mt)
    return

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

def print_offset(s, offset, offsetstart):
    col, _ = os.get_terminal_size()
    indices = list(range(0, len(s), col - offset))
    parts = [s[i:j] for i,j in zip(indices, indices[1:]+[None])]
    for i in range(len(parts)):
        if i >= offsetstart:
            parts[i] = (offset * " ") + parts[i]
    print("\n".join(parts))

