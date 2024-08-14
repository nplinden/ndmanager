import argparse as ap
import shutil
from pathlib import Path

from ndmanager.API.data import NDM_DIR


def init(args: ap.Namespace):
    if NDM_DIR.exists():
        if args.force:
            shutil.rmtree(NDM_DIR)
        else:
            raise ValueError(f"{NDM_DIR} directory already exists.")
    NDM_DIR.mkdir(parents=True)
