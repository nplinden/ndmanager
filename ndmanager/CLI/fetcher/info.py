import argparse as ap
import os
import textwrap

from ndmanager.API.data import ENDF6_LIBS
from ndmanager.API.utils import footer, header


def info(args: ap.Namespace):
    col, _ = os.get_terminal_size()

    def wrap(string, initial_indent=""):
        toprint = textwrap.wrap(
            string, initial_indent=initial_indent, subsequent_indent=26 * " ", width=col
        )
        toprint = "\n".join(toprint)
        return toprint

    lst = []
    for lib in args.library:
        dico = ENDF6_LIBS[lib]
        lst.append(header(lib))
        lst.append(wrap(f"{'Fancy name:':<25} {dico['fancyname']}"))
        lst.append(wrap(f"{'Source:':<25} {dico['source']}"))
        lst.append(wrap(f"{'Homepage:':<25} {dico['homepage']}"))
        subs = "  ".join(dico["sublibraries"])
        lst.append(wrap(f"{'Available Sublibraries:':<25} {subs}"))
        if "index" in dico:
            index = dico["index"]
            lst.append(wrap(f"{'Index: ':<25} {index[0]}"))
            for s in index[1:]:
                lst.append(wrap(s, initial_indent=26 * " "))
        lst.append(footer())
    print("\n".join(lst))
