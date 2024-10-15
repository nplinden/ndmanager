import os
from pathlib import Path
import yaml

if "NDMANAGER_CONFIG" in os.environ:
    NDMANAGER_CONFIG = Path(os.environ["NDMANAGER_CONFIG"]).absolute()
else:
    NDMANAGER_CONFIG = Path.home() / ".config/ndmanager/"

if (settings_path := (NDMANAGER_CONFIG / "settings.yml")).exists():
    settings = yaml.safe_load(open(settings_path, "r"))
else:
    settings = {}

if "NDMANAGER_ENDF6" in os.environ:
    NDMANAGER_ENDF6 = Path(os.environ["NDMANAGER_ENDF6"]).absolute()
elif "NDMANAGER_ENDF6" in settings:
    NDMANAGER_ENDF6 = Path(settings["NDMANAGER_ENDF6"]).absolute()
else:
    NDMANAGER_ENDF6 = None

if "NDMANAGER_HDF5" in os.environ:
    NDMANAGER_HDF5 = Path(os.environ["NDMANAGER_HDF5"]).absolute()
elif "NDMANAGER_HDF5" in settings:
    NDMANAGER_HDF5 = Path(settings["NDMANAGER_HDF5"]).absolute()
else:
    NDMANAGER_HDF5 = None

if "NDMANAGER_CHAINS" in os.environ:
    NDMANAGER_CHAINS = Path(os.environ["NDMANAGER_CHAINS"]).absolute()
elif "NDMANAGER_CHAINS" in settings:
    NDMANAGER_CHAINS = Path(settings["NDMANAGER_CHAINS"]).absolute()
else:
    NDMANAGER_CHAINS = None