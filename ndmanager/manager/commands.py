from pathlib import Path
import argparse as ap
import shutil

def ndm_init(args: ap.Namespace):
    dotfile = Path.home() / ".ndmanager"

    if dotfile.exists():
        if args.force:
            shutil.rmtree(dotfile)
        else:
            raise ValueError(f"{dotfile} directory already exists.")
    dotfile.mkdir(parents=True)