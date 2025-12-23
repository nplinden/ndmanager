"""A module to retrieve user defined data to determine where to write the
libraries
"""

import os
from pathlib import Path

if "NDMANAGER_ENDF6" in os.environ:
    NDMANAGER_ENDF6 = Path(os.environ["NDMANAGER_ENDF6"]).absolute()
else:
    NDMANAGER_ENDF6 = Path.home() / "ndmanager/endf6"

if "NDMANAGER_HDF5" in os.environ:
    NDMANAGER_HDF5 = Path(os.environ["NDMANAGER_HDF5"]).absolute()
else:
    NDMANAGER_HDF5 = Path.home() / "ndmanager/hdf5"

if "NDMANAGER_CHAINS" in os.environ:
    NDMANAGER_CHAINS = Path(os.environ["NDMANAGER_CHAINS"]).absolute()
else:
    NDMANAGER_CHAINS = Path.home() / "ndmanager/chains"

NDMANAGER_ENDF6.mkdir(parents=True, exist_ok=True)
NDMANAGER_HDF5.mkdir(parents=True, exist_ok=True)
NDMANAGER_CHAINS.mkdir(parents=True, exist_ok=True)
