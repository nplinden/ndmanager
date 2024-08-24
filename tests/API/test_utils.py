import pytest

from ndmanager.API.utils import get_url_paths, download_endf6, fetch_endf6
from pathlib import Path

decay_H1_endf6 = """Retrieved by E4-util: 2018/02/07,17:58:34                            1 0  0    0
 1.001000+3 9.991673-1         -1          0          0          0   2 1451    1
 0.000000+0 0.000000+0          0          0          0          6   2 1451    2
 0.000000+0 0.000000+0          0          0          4          8   2 1451    3
 0.000000+0 0.000000+0          0          0         17          2   2 1451    4
  1-H -  1  NNDC       EVAL-APR11 Conversion from N. Wallet Cards    2 1451    5
 /ENSDF/              DIST-FEB18                       20111222      2 1451    6
----ENDF/B-VIII.0     Material    2                                  2 1451    7
-----RADIOACTIVE DECAY DATA                                          2 1451    8
------ENDF-6 FORMAT                                                  2 1451    9
*********************** Begin Description ***********************    2 1451   10
**         ENDF/B-VII.1 RADIOACTIVE DECAY DATA FILE            **    2 1451   11
** Produced at the NNDC from the Nuclear Wallet Cards database **    2 1451   12
**                      Author: J.K. Tuli                      **    2 1451   13
**               Translated into ENDF format by:               **    2 1451   14
**    T.D. Johnson, E.A. McCutchan and A.A. Sonzogni, 2011     **    2 1451   15
*****************************************************************    2 1451   16
Parent Excitation Energy: 0.0000                                     2 1451   17
Parent Spin & Parity: 1/2+                                           2 1451   18
Parent half-life: STABLE                                             2 1451   19
Abundance: 99.985% 1                                                 2 1451   20
************************ End Description ************************    2 1451   21
                                1        451         23          0   2 1451   22
                                8        457          5          0   2 1451   23
 0.000000+0 0.000000+0          0          0          0          0   2 1  099999
 0.000000+0 0.000000+0          0          0          0          0   2 0  0    0
 1.001000+3 9.991673-1          0          0          1          0   2 8457    1
 0.000000+0 0.000000+0          0          0          6          0   2 8457    2
 0.000000+0 0.000000+0 0.000000+0 0.000000+0 0.000000+0 0.000000+0   2 8457    3
 5.000000-1 1.000000+0          0          0          6          0   2 8457    4
 0.000000+0 0.000000+0 0.000000+0 0.000000+0 0.000000+0 0.000000+0   2 8457    5
                                                                     2 8  099999
                                                                     2 0  0    0
                                                                     0 0  0    0
                                                                    -1 0  0    0
"""


def test_get_url_paths():
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


def test_download_endf6():
    directory = Path("pytest-artifacts/API/test_utils/")
    download_endf6("endfb8", "decay", "H1", directory / "decay-H1.endf6")
    with open(directory / "decay-H1.endf6", "r", encoding="utf-8") as f:
        candidate = f.read()
    assert candidate == decay_H1_endf6


def test_fetch_endf6():
    candidate = fetch_endf6("endfb8", "decay", "H1")
    assert candidate == decay_H1_endf6
