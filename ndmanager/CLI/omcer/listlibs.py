import os
import textwrap

from ndmanager.data import (
    OPENMC_LIBS,
    OPENMC_NUCLEAR_DATA,
)
from ndmanager.format import header


def listlibs(*args):
    col, _ = os.get_terminal_size()
    lst = [header("Installable Libraries")]
    for family, dico in OPENMC_LIBS.items():
        for libname, libdict in dico.items():
            fancyname = libdict["fancyname"]
            if (OPENMC_NUCLEAR_DATA / family / libname).exists():
                check = "✓"
            else:
                check = " "
            s = f"{family}/{libname}"
            s = f"{s:<16} {fancyname:<15} [{check}]: {libdict['info']}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=38 * " ", width=col
            )
            lst.append("\n".join(s))
    lst.append("")
    lst.append(header("Custom Libraries"))
    s = " ".join(
        [f"{s.name:<15}" for s in list((OPENMC_NUCLEAR_DATA / "custom").glob("*"))]
    )
    s = textwrap.wrap(s, width=col)
    lst.append("\n".join(s))
    print("\n".join(lst))
