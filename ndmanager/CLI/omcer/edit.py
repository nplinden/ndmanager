"""Definition and parser for the `ndo sn301` command"""

import argparse as ap
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

import numpy as np
from h5py import File

from ndmanager.env import NDMANAGER_HDF5
from ndmanager.CLI.parser import Command


class NdoSn301Command(Command):
    """Define the `ndo sn301` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndo sn301' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
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
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace):
        """Substitute negative MT301 cross section values in a target library,
        from a set of source libaries

        Args:
            args (ap.Namespace): The argparse object containing the command line argument
        """
        target = NDMANAGER_HDF5 / args.target / "cross_sections.xml"
        sources = [NDMANAGER_HDF5 / s / "cross_sections.xml" for s in args.sources]
        replace_negatives_in_lib(target, sources, 301, dryrun=args.dryrun, verbose=True)


def overwrite_one_temp(source: File, target: File, nuclide: str, mt: int, t: str):
    """Substitute cross-section values for a given (nuclide, reaction, temperature) tuple
    from a source HDF5 file in a target HDF5.

    Args:
        source (h5py.File): The opened source file
        target (h5py.File): The opened target file
        nuclide (str): The name of the nuclide
        mt (int): The MT number of the reaction
        t (str): The name of the temperature node
    """
    target_grid = target[f"{nuclide}/energy/{t:d}K"][...]
    target_attrs = target[f"{nuclide}/reactions/reaction_{mt:03d}/{t}K/xs"].attrs

    source_grid = source[f"{nuclide}/energy/{t:d}K"][...]
    source_xs = source[f"{nuclide}/reactions/reaction_{mt:03d}/{t}K/xs"][...]

    replacement = np.interp(target_grid, source_grid, source_xs)
    del target[f"{nuclide}/reactions/reaction_{mt:03d}/{t}K/xs"]
    target[f"{nuclide}/reactions/reaction_{mt:03d}/{t}K/xs"] = replacement
    for k, v in target_attrs.items():
        target[f"{nuclide}/reactions/reaction_{mt:03d}/{t}K/xs"].attrs[k] = v


def overwrite(nuclide: str, mt: int, sourcefile: str, targetfile: str):
    """Substitute cross-section values for a given (nuclide, reaction) couple
    from a source HDF5 file in a target HDF5.

    Args:
        nuclide (str): The name of the nuclide
        mt (int): The MT number of the reaction
        sourcefile (str): The path to the source file
        targetfile (str): The path to the target file

    Raises:
        ValueError: If the temperatures available in the source and target file
                    are different
    """
    with File(sourcefile, "r") as source, File(targetfile, "r+") as target:
        source_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]
        target_rgroup = source[f"{nuclide}/reactions/reaction_{mt:03d}/"]

        source_temperatures = [int(T[:-1]) for T in source_rgroup.keys() if "K" in T]
        target_temperatures = [int(T[:-1]) for T in target_rgroup.keys() if "K" in T]

        for t in target_temperatures:
            if t not in source_temperatures:
                raise ValueError(
                    f"Temperature {t} not available for MT={mt} in {sourcefile}"
                )

        for t in target_temperatures:
            overwrite_one_temp(source, target, nuclide, mt, t)


def find_negative(matpath: str, mt: int) -> Dict[str, Dict[str, str | List[str]]]:
    """Find negative cross sections in a nuclear data library HDF5 file

    Args:
        matpath (str): Path to the HDF5 file
        mt (int): The MT number of the reaction

    Returns:
        Dict[str, Dict[str, str | List[str]]]: Dictionnary of negative values
    """
    result = {}
    with File(matpath, "r") as f:
        nuclides = list(f.keys())
        for nuclide in nuclides:
            try:
                rgroup = f[f"{nuclide}/reactions/reaction_{mt:03d}/"]
            except KeyError:
                continue
            temperatures = [T for T in rgroup.keys() if "K" in T]
            negatives = []
            for t in temperatures:
                xs = f[f"{nuclide}/reactions/reaction_{mt:03d}/{t}/xs"][...]
                if np.any(xs < 0):
                    negatives.append(t)
            if negatives:
                result[nuclide] = {"path": matpath, "temperatures": negatives}
    return result


def find_negative_in_lib(
    libpath: str, mt: int
) -> Dict[str, Dict[str, str | List[str]]]:
    """Find negative cross sections in a nuclear data library xml file

    Args:
        libpath (str): Path to a cross_sections.xml file
        mt (int): The MT number of the reaction

    Returns:
        Dict[str, Dict[str, str | List[str]]]: Dictionnary of negative values
    """
    plib = Path(libpath)
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


def set_negative_to_zero(matpath: str, mt: int) -> None:
    """Set negative cross-sections to zero in the file

    Args:
        matpath (str): The path to the file
        mt (int): The MT number of the reaction
    """
    with File(matpath, "r+") as f:
        for nuclide in f.keys():
            try:
                rgroup = f[f"{nuclide}/reactions/reaction_{mt:03d}/"]
            except KeyError:
                return
            temperatures = [T for T in rgroup.keys() if "K" in T]
            for t in temperatures:
                xs = f[f"{nuclide}/reactions/reaction_{mt:03d}/{t}/xs"][...]
                f[f"{nuclide}/reactions/reaction_{mt:03d}/{t}/xs"][xs < 0] = 0.0


def set_negative_to_zero_in_lib(libpath: str, mt: int) -> None:
    """Set negative cross-sections to zero in all files in the nuclear data
    library

    Args:
        libpath (str): The path to the cross_sections.xml file
        mt (int): The MT number of the reaction
    """
    plib = Path(libpath)
    root = ET.parse(plib).getroot()

    directorynode = root.find("directory")
    if directorynode is not None:
        directory = directorynode.text
    else:
        directory = ""

    for lib in root.findall("library"):
        if lib.attrib.get("type") == "neutron":
            libpath = plib.parent / directory / lib.attrib["path"]
            set_negative_to_zero(libpath, mt)


def find_nuclide_in_lib(libpath: str, nuclide: str) -> Path:
    """Find the path to an HDF5 material file from a cross_sections.xml file

    Args:
        libpath (str): Path to the cross_sections.xml file
        nuclide (str): Name of the desired nuclide

    Returns:
        Path: Path to the material file
    """
    plib = Path(libpath)
    root = ET.parse(plib).getroot()

    directorynode = root.find("directory")
    if directorynode is not None:
        directory = directorynode.text
    else:
        directory = ""

    for lib in root.findall("library"):
        if lib.attrib.get("type") == "neutron" and lib.attrib["materials"] == nuclide:
            return plib.parent / directory / lib.attrib["path"]
    return None


def replace_negatives_in_lib(
    target_path: str,
    source_paths: List[str],
    mt: int,
    dryrun: bool = False,
    verbose: bool = True,
) -> None:
    """Replace the negative cross-section values for a (nuclide, reaction)
    couple in a cross_sections.xml defined library.

    Args:
        target_path (str): Path to the target cross_sections.xml file
        source_paths (str): List of paths to the source cross_sections.xml files
        mt (int): The MT number of the reaction
        dryrun (bool, optional): Do not perform the substitution. Defaults to False.
        verbose (bool, optional): Additionnal log info. Defaults to True.
    """
    negatives = find_negative_in_lib(target_path, mt)
    source_negatives = {
        source: find_negative_in_lib(source, mt) for source in source_paths
    }

    for nuclide in negatives:
        found = False
        source = None
        target = None
        for sourcelib, sn in source_negatives.items():
            source = find_nuclide_in_lib(sourcelib, nuclide)
            target = find_nuclide_in_lib(target_path, nuclide)
            # Nuclide is not in source library
            if source is None:
                continue
            # Nuclide's xs is also negative in the source library
            if nuclide in sn:
                continue
            found = True
            if verbose:
                print(
                    f"Replacing\n\tnuclide={nuclide}\n\tmt={mt}"
                    "\n\ttarget={target}\n\tsource={source}"
                )
            if not dryrun:
                overwrite(nuclide, mt, source, target)

        if not found:
            if verbose:
                print(
                    f"No replacement found\n\tnuclide={nuclide}\n\tmt={mt}"
                    "\n\ttarget={target}\n\tsource={source}"
                )
            if not dryrun:
                set_negative_to_zero(target, mt)
