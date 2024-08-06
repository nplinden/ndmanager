from pathlib import Path
import argparse as ap

def ndm_init(args: ap.Namespace):
    dotfile = Path.home() / ".ndmanager"

    if dotfile.exists():
        if args.force:
            dotfile.unlink()
        else:
            raise ValueError(f"{dotfile} directory already exists.")
    dotfile.mkdir(parents=True)