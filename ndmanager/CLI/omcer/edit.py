import argparse as ap
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from h5py import File

from ndmanager.data import OPENMC_NUCLEAR_DATA


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


def replace_negatives_in_lib(targetlib, sources, mt, dryrun=False, verbose=True):
    negatives = find_negative_in_lib(targetlib, mt)
    source_negatives = {source: find_negative_in_lib(source, mt) for source in sources}

    for nuclide in negatives:
        found = False
        source = None
        target = None
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
                    print(
                        f"Replacing\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}"
                    )
                if not dryrun:
                    overwrite(nuclide, mt, source, target)
                continue
        if not found:
            if verbose:
                print(
                    f"No replacement found\n\tnuclide={nuclide}\n\tmt={mt}\n\ttarget={target}\n\tsource={source}"
                )
            if not dryrun:
                set_negative_to_zero(target, nuclide, mt)
    return


def sn301_parser(subparsers):
    parser = subparsers.add_parser(
        "sn301", help="Substitute negative MT=301 cross-section in HDF5 library"
    )
    parser.add_argument("--target", "-t", type=str, help="The library to fix")
    parser.add_argument(
        "--sources",
        "-s",
        action="extend",
        nargs="+",
        type=str,
        help="List of nuclear data libraries to choose from",
    )
    parser.add_argument(
        "--dryrun", help="Do not perform the substitution", action="store_true"
    )
    parser.set_defaults(func=sn301)


def sn301(args: ap.Namespace):
    target = OPENMC_NUCLEAR_DATA / args.target / "cross_sections.xml"
    sources = [OPENMC_NUCLEAR_DATA / s / "cross_sections.xml" for s in args.sources]
    replace_negatives_in_lib(target, sources, 301, dryrun=args.dryrun, verbose=True)
