import os
import textwrap

from ndmanager.data import ENDF6_LIBS, ENDF6_PATH
from ndmanager.format import footer, header


def listlibs(*args):
    col, _ = os.get_terminal_size()
    lst = []
    lst.append(header("Available libraries"))
    for lib in ENDF6_LIBS:
        fancyname = ENDF6_LIBS[lib]["fancyname"]
        if (ENDF6_PATH / lib).exists():
            check = "✓"
        else:
            check = " "
        s = f"{lib:<8} {fancyname:<15} [{check}]: {ENDF6_LIBS[lib]['info']}"
        s = textwrap.wrap(s, initial_indent="", subsequent_indent=30 * " ", width=col)
        lst.append("\n".join(s))
    lst.append(footer())
    print("\n".join(lst))
