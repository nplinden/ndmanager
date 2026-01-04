# pylint: disable=invalid-name
"""A module that defines and ENDF6 class to manipulate ENDF6 tapes."""

from pathlib import Path

from ndmanager.data import NSUB_IDS
from ndmanager.env import NDMANAGER_ENDF6
from ndmanager.nuclide import Nuclide


class Endf6:
    """A module that defines and ENDF6 class to manipulate ENDF6 tapes."""

    def __init__(self, filename: str | Path) -> None:
        """Instanciate an Endf6 object using a path to a tape.

        Args:
            filename (str | Path): Path to an ENDF6 tape

        """
        self.filename = filename
        self.nuclide = Nuclide.from_file(filename)
        with Path(filename).open(encoding="utf-8") as f:
            for _ in range(4):
                line = f.readline()
            NSUB = int(line[46:56])
        self.sublibrary = NSUB_IDS[NSUB]


def get_endf6(libname: str, sub: str, nuclide: str) -> Path:
    """Get the path to a ENDF6 tape stored in the NDManager database.

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
        msg = f"Library '{libname}' does not exist"
        raise ValueError(msg)
    p = p / sub
    if not p.exists():
        msg = f"No {sub} sublibrary available for '{libname}'"
        raise ValueError(msg)
    p = p / f"{nuclide}"
    if p.suffix != ".endf6":
        p = p.parent / (p.name + ".endf6")
    if not p.exists():
        msg = f"No {nuclide} nuclide available for '{libname}', '{sub}"
        raise ValueError(msg)
    return p


def list_endf6(sublibrary: str, params: dict[str, str]) -> dict[str, Path]:
    """List the paths to ENDF6 evaluations necessary to build the cross-sections and depletion chains.

    Args:
        sublibrary (str): The sublibrary type (n, decay, nfpy).
        params (Dict[str, str]): The parameters in the form of a dictionnary.

    Returns:
        Dict[str, Path]: A dictionnary that associates nuclide names to ENDF6 paths.

    """
    base = params["base"]
    omit = params.get("omit", "").split()
    add = params.get("add", {})

    base_paths = (NDMANAGER_ENDF6 / base / sublibrary).glob("*.endf6")
    base_dict = {Nuclide.from_file(p).name: p for p in base_paths}

    # Remove unwanted evaluations
    for nuclide in omit:
        base_dict.pop(Nuclide.from_name(nuclide).name, None)

    # Remove neutron evaluations if they are present.
    base_dict.pop("n1", None)
    base_dict.pop("nn1", None)
    base_dict.pop("N1", None)

    # Add custom evaluations.
    # Overwrite if the main library already provides them.
    guest_dict = {}
    for guestlib, _nuclides in add.items():
        nuclides = _nuclides.split()
        for nuclide in nuclides:
            p = NDMANAGER_ENDF6 / guestlib / sublibrary / f"{nuclide}.endf6"
            if not p.exists():
                msg = f"Nuclide {nuclide} is not available in the {guestlib} library."
                raise ValueError(msg)
            guest_dict[nuclide] = p
        base_dict |= guest_dict

    return base_dict
