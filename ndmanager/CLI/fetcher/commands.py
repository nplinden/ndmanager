import argparse as ap
import os
import shutil
import time
from functools import reduce
from itertools import cycle, product
from multiprocessing import Pool
import textwrap

from tabulate import tabulate

from ndmanager.API.data import ENDF6_LIBS, ENDF6_PATH, SUBLIBRARIES_SHORTLIST
from ndmanager.API.utils import clear_line, header, footer
from ndmanager.CLI.fetcher.download import download


def ndf_clone(args: ap.Namespace):
    source = ENDF6_PATH / args.source
    target = ENDF6_PATH / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)


def ndf_remove(args: ap.Namespace):
    libraries = [ENDF6_PATH / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)


def ndf_avail(*args):
    col, _ = os.get_terminal_size()
    print(f"{'  Available ENDF6 Libraries  ':{'-'}{'^'}{col}}")
    toprint = "  ".join([p.name for p in ENDF6_PATH.glob("*")])
    print(toprint)
    print("\n\n")


def ndf_list(*args):
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


def ndf_info(args: ap.Namespace):
    col, _ = os.get_terminal_size()

    def wrap(string, initial_indent=""):
        toprint = textwrap.wrap(
            string, initial_indent=initial_indent, subsequent_indent=26 * " ", width=col
        )
        toprint = "\n".join(toprint)
        return toprint

    info = []
    for lib in args.library:
        dico = ENDF6_LIBS[lib]
        info.append(header(lib))
        info.append(wrap(f"{'Fancy name:':<25} {dico['fancyname']}"))
        info.append(wrap(f"{'Source:':<25} {dico['source']}"))
        info.append(wrap(f"{'Homepage:':<25} {dico['homepage']}"))
        subs = "  ".join(dico["sublibraries"])
        info.append(wrap(f"{'Available Sublibraries:':<25} {subs}"))
        if "index" in dico:
            index = dico["index"]
            info.append(wrap(f"{'Index: ':<25} {index[0]}"))
            for s in index[1:]:
                info.append(wrap(s, initial_indent=26 * " "))
        info.append(footer())
    print("\n".join(info))


def list_reshape(lst, shape):
    if len(shape) == 1:
        return lst
    n = reduce(lambda x, y: x * y, shape[1:])
    return [
        list_reshape(lst[i * n : (i + 1) * n], shape[1:]) for i in range(len(lst) // n)
    ]


def ndf_install(args: ap.Namespace):
    libs = args.libraries
    if args.sub is not None:
        sub = args.sub
    else:
        sub = SUBLIBRARIES_SHORTLIST
    stargs = list(product(libs, sub))

    table = [[lib] + ["..." for __ in sub] for lib in libs]
    print(tabulate(table, [] + sub, tablefmt="rounded_outline"))

    with Pool() as p:
        results = [p.apply_async(download, a) for a in stargs]
        c = cycle([".", "..", "..."])

        while True:
            time.sleep(0.5)
            symb = next(c)
            isdone = [r.ready() for r in results]
            symbols = [r.get() if r.ready() else symb for r in results]

            progress = []
            for ilib, lib in enumerate(libs):
                left, right = ilib * len(sub), (ilib + 1) * len(sub)
                progress.append([lib] + symbols[left:right])

            clear_line(len(libs) + 4)
            print(tabulate(progress, [] + sub, tablefmt="rounded_outline"))
            if all(isdone):
                break
