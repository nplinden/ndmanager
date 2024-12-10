"""Some utility function to compute ENDF6 tape SHA1"""

import hashlib
from typing import Dict

from ndmanager.API.endf6 import get_endf6
from ndmanager.env import NDMANAGER_ENDF6


def compute_file_sha1(filename: str) -> str:
    """Compute the SHA1 value of a file given its path.

    Args:
        Path to a file.
    """
    BUF_SIZE = 65536  # 64 kBi
    sha1 = hashlib.sha1()
    with open(filename, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def compute_tape_sha1(libname: str, sub: str, nuclide: str) -> Dict[str, str]:
    """Compute the SHA1 hash of a tape stored in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format. For TSL tapes,
                       the name of the tape

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tape as key and
                        SHA1 has as value

    """
    tape = get_endf6(libname, sub, nuclide)
    sha1 = compute_file_sha1(tape)
    return {f"{libname}/{sub}/{nuclide}": sha1}


def compute_sublib_sha1(libname: str, sub: str) -> Dict[str, str]:
    """Compute the SHA1 hash of all tapes in a sublibrary in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    subdir = NDMANAGER_ENDF6 / libname / sub
    results = {}
    for tape in subdir.iterdir():
        results |= compute_tape_sha1(libname, sub, tape.stem)
    return results


def compute_lib_sha1(libname: str) -> Dict[str, str]:
    """Compute the SHA1 hash of all tapes in a library in the NDManager database

    Args:
        libname (str): The name of the desired evaluation

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    libdir = NDMANAGER_ENDF6 / libname
    results = {}
    for sub in libdir.iterdir():
        results |= compute_sublib_sha1(libname, sub.name)
    return results


def compute_sha1(libname: str, sub: str = None, nuclide: str = None) -> Dict[str, str]:
    """Compute the SHA1 hash of tapes in a library in the NDManager database.
    If a sublibrary is specified, only tapes in that sublibrary will be computed.
    If a nuclide is also specified, only the corresponding tape will be computed.

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    if sub is None and nuclide is not None:
        raise ValueError("You can't specify a nuclide without a sublibrary")
    if nuclide is None:
        if sub is None:
            return compute_lib_sha1(libname)
        return compute_sublib_sha1(libname, sub)
    return compute_tape_sha1(libname, sub, nuclide)
