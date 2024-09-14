"""Some utility functions"""
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
