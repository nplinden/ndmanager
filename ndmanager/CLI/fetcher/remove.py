import argparse as ap
import shutil

from ndmanager.API.data import ENDF6_PATH


def remove(args: ap.Namespace):
    libraries = [ENDF6_PATH / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)
