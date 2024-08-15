import os
import textwrap

from ndmanager.API.data import ENDF6_LIBS, ENDF6_PATH


def listlibs(*args):
    col, _ = os.get_terminal_size()
    lst = []
    for lib in ENDF6_LIBS:
        fancyname = ENDF6_LIBS[lib]["fancyname"]
        if (ENDF6_PATH / lib).exists():
            check = "✓"
        else:
            check = " "
        s = f"{lib:<8} {fancyname:<15} [{check}]: {ENDF6_LIBS[lib]['info']}"
        s = textwrap.wrap(s, initial_indent="", subsequent_indent=30 * " ", width=col)
        lst.append("\n".join(s))
    print("\n".join(lst))