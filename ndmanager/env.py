"""A module to retrieve user defined data to determine where to write the
libraries
"""

import os
from pathlib import Path

import yaml

if "NDMANAGER_CONFIG" in os.environ:
    NDMANAGER_CONFIG = Path(os.environ["NDMANAGER_CONFIG"]).absolute()
else:
    NDMANAGER_CONFIG = Path.home() / ".config/ndmanager/"

if (settings_path := NDMANAGER_CONFIG / "settings.yml").exists():
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)
else:
    settings = {}

if "NDMANAGER_ENDF6" in os.environ:
    NDMANAGER_ENDF6 = Path(os.environ["NDMANAGER_ENDF6"]).absolute()
elif "NDMANAGER_ENDF6" in settings:
    NDMANAGER_ENDF6 = Path(settings["NDMANAGER_ENDF6"]).absolute()
else:
    NDMANAGER_ENDF6 = NDMANAGER_CONFIG / "endf6"

if "NDMANAGER_HDF5" in os.environ:
    NDMANAGER_HDF5 = Path(os.environ["NDMANAGER_HDF5"]).absolute()
elif "NDMANAGER_HDF5" in settings:
    NDMANAGER_HDF5 = Path(settings["NDMANAGER_HDF5"]).absolute()
else:
    NDMANAGER_HDF5 = NDMANAGER_CONFIG / "hdf5"

if "NDMANAGER_CHAINS" in os.environ:
    NDMANAGER_CHAINS = Path(os.environ["NDMANAGER_CHAINS"]).absolute()
elif "NDMANAGER_CHAINS" in settings:
    NDMANAGER_CHAINS = Path(settings["NDMANAGER_CHAINS"]).absolute()
else:
    NDMANAGER_CHAINS = NDMANAGER_CONFIG / "chains"

if "NDMANAGER_SAMPLES" in os.environ:
    NDMANAGER_SAMPLES = Path(os.environ["NDMANAGER_SAMPLES"]).absolute()
elif "NDMANAGER_SAMPLES" in settings:
    NDMANAGER_SAMPLES = Path(settings["NDMANAGER_SAMPLES"]).absolute()
else:
    NDMANAGER_SAMPLES = NDMANAGER_CONFIG / "samples"

if "NDMANAGER_COV" in os.environ:
    NDMANAGER_COV = Path(os.environ["NDMANAGER_COV"]).absolute()
elif "NDMANAGER_COV" in settings:
    NDMANAGER_COV = Path(settings["NDMANAGER_COV"]).absolute()
else:
    NDMANAGER_COV = NDMANAGER_CONFIG / "cov"
