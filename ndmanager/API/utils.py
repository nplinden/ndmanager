import os
from typing import List

from ndmanager.API.data import ENDF6_PATH, OPENMC_NUCLEAR_DATA


def clear_line(n: int = 1):
    """Move the print cursor up n lines.

    Args:
        n (int, optional): Number of lines the cursor will be moved up. Defaults to 1.
    """
    LINE_UP = "\033[1A"
    LINE_CLEAR = "\x1b[2K"
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)


def print_offset(s: str, offset: int, offsetstart: int):
    """Print the string with an integer valued offset on the left. offsetstart
    if useful for multiline string where the first line should not be offset.

    Args:
        s (string): The string to print.
        offset (int): The left offset value.
        offsetstart (int): Line number to start offsetting on.
    """
    col, _ = os.get_terminal_size()
    indices = list(range(0, len(s), col - offset))
    parts = [s[i:j] for i, j in zip(indices, indices[1:] + [None])]
    for i in range(len(parts)):
        if i >= offsetstart:
            parts[i] = (offset * " ") + parts[i]
    print("\n".join(parts))


def set_ndl(libname: str):
    """Set openmc.config["cross_section"] value to the path to the
    cross_sections.xml file of the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """
    import openmc

    if libname[-4:] == ".xml":
        openmc.config["cross_sections"] = libname
    else:
        p = OPENMC_NUCLEAR_DATA / libname / "cross_sections.xml"
        if p.exists():
            openmc.config["cross_sections"] = p
        else:
            raise FileNotFoundError(f"Invalid library name '{libname}'")


def set_chain(libname: str):
    """Set openmc.config["chain_file"] value to the path to the chain file of
    the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """
    import openmc

    if libname[-4:] == ".xml":
        openmc.config["chain_file"] = libname
    else:
        p = OPENMC_NUCLEAR_DATA / libname
        if not p.exists():
            raise FileNotFoundError(f"Invalid library name '{libname}'")
        p = p / "chain.xml"
        if not p.exists():
            raise FileNotFoundError(f"No chain available for library '{libname}'")
        openmc.config["chain_file"] = p


def set_nuclear_data(libname: str, chain: str = False):
    """Set openmc.config["chain_file"] and openmc.config["cross_sections"]
    value to the corresponding paths for the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.
        chain (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """
    set_ndl(libname)
    if chain:
        set_chain(libname)


def get_endf6(libname: str, sub: str, nuclide: str):
    p = ENDF6_PATH / libname
    if not p.exists():
        raise ValueError(f"Library '{libname}' does not exist")
    p = p / sub
    if not p.exists():
        raise ValueError(f"No {sub} sublibrary available for '{libname}'")
    p = p / f"{nuclide}.endf6"
    if not p.exists():
        raise ValueError(f"No {nuclide} nuclide available for '{libname}', '{sub}")
    return p


def check_nuclear_data(libpath: str, nuclides: List[str]):
    import openmc

    lib = openmc.data.DataLibrary.from_xml(libpath)
    missing = []
    for nuclide in nuclides:
        if lib.get_by_material(nuclide) is None:
            missing.append(nuclide)
    if missing:
        raise ValueError(
            f"Nuclear Data Library lacks the following required nuclides: {missing}"
        )
