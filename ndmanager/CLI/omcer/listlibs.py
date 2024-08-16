import os
import textwrap

from ndmanager.API.data import (
    OPENMC_LIBS,
    OPENMC_NUCLEAR_DATA,
)
from ndmanager.API.utils import footer, header


def listlibs(*args):
    col, _ = os.get_terminal_size()
    lst = [header("Available libraries")]
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
    lst.append(footer())
    print("\n".join(lst))
