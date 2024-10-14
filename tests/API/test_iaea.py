import hashlib
from pathlib import Path

import pytest
import requests

from ndmanager.API.iaea import (download_endf6, fetch_endf6, get_url_paths)
from ndmanager.data import TAPE_SHA1


def test_get_url_paths():
    # Cases where it does not work
    with pytest.raises(requests.HTTPError):
        get_url_paths("https://httpbin.org/status/404")
    with pytest.raises(requests.ReadTimeout):
        get_url_paths("https://httpbin.org/delay/10")

    # Cases where it works
    urls = get_url_paths(
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/", "zip"
    )
    reference = [
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9237_92-U-238.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9637_96-Cm-244.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9643_96-Cm-246.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9649_96-Cm-248.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9855_98-Cf-250.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9861_98-Cf-252.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9913_99-Es-253.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9935_100-Fm-254.zip",
        "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/sfpy/sfpy_9937_100-Fm-256.zip",
    ]
    assert urls == reference


# def test_download_endf6():
#     directory = Path("pytest-artifacts/API/test_utils/")

#     download_endf6("endfb8", "decay", "H1", directory / "decay-H1.endf6")
#     sha1 = hashlib.sha1()
#     with open(directory / "decay-H1.endf6", "rb") as f:
#         data = f.read()
#         sha1.update(data)
#     assert sha1.hexdigest() == TAPE_SHA1["endfb8"]["endfb8/decay/H1"]


# def test_fetch_endf6():
#     ascii = fetch_endf6("endfb8", "decay", "H1")
#     data = ascii.encode()
#     sha1 = hashlib.sha1()
#     sha1.update(data)
#     assert sha1.hexdigest() == TAPE_SHA1["endfb8"]["endfb8/decay/H1"]
