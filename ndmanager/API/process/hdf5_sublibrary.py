import abc
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HDF5Sublibrary:
    target: str
    path: Path
    logpath: Path

    @abc.abstractmethod
    def process(self):
        return

    def get_logger(self):
        logger = logging.getLogger(self.logpath.stem)
        handler = logging.FileHandler(self.logpath)
        format = "%(asctime)s | %(levelname)-8s | %(message)s"
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("INFO")

        def showwarning(message, *args, **kwargs):
            logger.warning(message)

        warnings.showwarning = showwarning
        return logger

