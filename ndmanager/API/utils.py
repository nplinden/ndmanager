import os
from ndmanager.API.data import OPENMC_NUCLEAR_DATA, ENDF6_PATH


def clear_line(n=1):
    LINE_UP = "\033[1A"
    LINE_CLEAR = "\x1b[2K"
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
        p = OPENMC_NUCLEAR_DATA / libname / "cross_sections.xml"
        if p.exists():
            openmc.config["cross_sections"] = p
        else:
            raise FileNotFoundError(f"Invalid library name '{libname}'")


def set_chain(libname):
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


def set_nuclear_data(libname, chain=False):
    set_ndl(libname)
    if chain:
        set_chain(libname)


def get_endf6(libname, sub, nuclide):
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


def check_nuclear_data(libpath, nuclides):
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
