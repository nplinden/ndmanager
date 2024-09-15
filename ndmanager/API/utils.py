"""Some utility functions"""

from typing import Dict

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import NDMANAGER_ENDF6


def get_endf6(libname: str, sub: str, nuclide: str):
    """Get the path to a ENDF6 tape stored in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format

    Raises:
        ValueError: The library does not exist
        ValueError: The sublibrary is not available for the library
        ValueError: The nuclide is not available in the sublibrary

    Returns:
        pathlib.Path: The path to the library
    """
    p = NDMANAGER_ENDF6 / libname
    if not p.exists():
        raise ValueError(f"Library '{libname}' does not exist")
    p = p / sub
    if not p.exists():
        raise ValueError(f"No {sub} sublibrary available for '{libname}'")
    p = p / f"{nuclide}"
    if not p.suffix == ".endf6":
        p = p.parent / (p.name + ".endf6")
    if not p.exists():
        raise ValueError(f"No {nuclide} nuclide available for '{libname}', '{sub}")
    return p


def list_endf6(sublibrary: str, params: Dict[str, str]):
    """List the paths to ENDF6 evaluations necessary to build the cross-sections
    and depletion chains.

    Args:
        sublibrary (str): The sublibrary type (n, decay, nfpy).
        params (Dict[str, str]): The parameters in the form of a dictionnary.

    Returns:
        Dict[str, Path]: A dictionnary that associates nuclide names to ENDF6 paths.
    """
    basis = params["basis"]
    ommit = params.get("ommit", "").split()
    add = params.get("add", {})

    basis_paths = (NDMANAGER_ENDF6 / basis / sublibrary).glob("*.endf6")
    basis_dict = {Nuclide.from_file(p).name: p for p in basis_paths}

    # Remove unwanted evaluations
    for nuclide in ommit:
        basis_dict.pop(Nuclide.from_name(nuclide).name, None)

    # Remove neutron evaluations if they are present.
    basis_dict.pop("n1", None)
    basis_dict.pop("nn1", None)
    basis_dict.pop("N1", None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    guest_dict = {}
    for guestlib, _nuclides in add.items():
        nuclides = _nuclides.split()
        for nuclide in nuclides:
            p = NDMANAGER_ENDF6 / guestlib / sublibrary / f"{nuclide}.endf6"
            if not p.exists():
                raise ValueError(
                    f"Nuclide {nuclide} is not available in the {guestlib} library."
                )
            guest_dict[nuclide] = p
        basis_dict |= guest_dict

    return basis_dict
