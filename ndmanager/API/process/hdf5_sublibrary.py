"""A generic class to manage libraries of OpenMC HDF5 data files"""

import abc
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HDF5Sublibrary:
    """A generic class to manage libraries of OpenMC HDF5 data files"""

    target: str
    path: Path
    logpath: Path

    @abc.abstractmethod
    def process(self):
        """An HDF5Sublibrary should define a process method"""
        raise NotImplementedError(
            "Can't use the process method directly on a HDF5Sublibrary object"
        )

    def get_logger(self):
        """Create a new logger and return it

        Returns:
            logging.Logger: The logger object
        """
        logger = logging.getLogger(self.logpath.stem)
        handler = logging.FileHandler(self.logpath)
        fmt = "%(asctime)s [%(levelname)-8s] %(message)s"
        formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("INFO")

        def showwarning(message, *args, **kwargs):
            logger.warning(message)

        warnings.showwarning = showwarning
        return logger
