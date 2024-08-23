"""A few utility functions"""
from typing import Dict
from ndmanager.API.nuclide import Nuclide
from ndmanager.data import ENDF6_PATH


def list_endf6(sublibrary: str, params: Dict[str, str]):
    """List the paths to ENDF6 evaluations necessary to build the cross sections
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

    for nuclide in ommit:
        if nuclide in add:
            raise ValueError("A nuclide can't be both ommited and added.")

    basis_paths = (ENDF6_PATH / basis / sublibrary).glob("*.endf6")
    basis_dict = {Nuclide.from_file(p).name: p for p in basis_paths}

    # Remove unwanted evaluations
    for nuclide in ommit:
        basis_dict.pop(nuclide, None)

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
            p = ENDF6_PATH / guestlib / sublibrary / f"{nuclide}.endf6"
            if not p.exists():
                raise ValueError(
                    f"Nuclide {nuclide} is not available in the {guestlib} library."
                )
            guest_dict[nuclide] = p
        basis_dict |= guest_dict

    return basis_dict
