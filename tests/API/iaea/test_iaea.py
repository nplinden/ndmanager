from ndmanager.env import NDMANAGER_CONFIG
from ndmanager.API.iaea import IAEA, IAEALibrary
from ndmanager.API.sha1 import compute_file_sha1

import pytest

CACHE_SHA1 = "4011474e33ff944287932b53a441a8fef21e53c3"

def test_iaea():
    # Build without cache, tests from_website
    assert not IAEA.is_cached()
    iaea = IAEA(nocache=True)
    sha1 = compute_file_sha1(NDMANAGER_CONFIG / "IAEA_cache.json")
    assert sha1 == CACHE_SHA1
    assert IAEA.is_cached()

    # Build with cache, tests from_json and to_json
    iaea = IAEA()
    iaea.to_json("pytest-artifacts/IAEA_cache_bis.json")
    sha1 = compute_file_sha1("pytest-artifacts/IAEA_cache_bis.json")
    assert sha1 == CACHE_SHA1

    e = iaea["endfb8"]
    assert isinstance(e, IAEALibrary)

    iaea["endfb8-bis"] = iaea["endfb8"]
    e = iaea["endfb8-bis"]
    assert isinstance(e, IAEALibrary)

    sublibraries = iaea.keys 
    sublibraries== ['ADS-2.0',
        'ADS-HE',
        'BROND-2-2',
        'BROND-3.1',
        'CENDL-2',
        'CENDL-3.1',
        'CENDL-3.2',
        'EAF-2010',
        'ENDF-B-VII.0',
        'ENDF-B-VII.1',
        'ENDF-B-VIII.0',
        'ENDF-B-VIII.1',
        'FENDL-2.1',
        'FENDL-3.1c',
        'FENDL-3.2',
        'FENDL-3.2b',
        'IAEA-Medical',
        'IAEA-PD-1999',
        'IAEA-PD-2019',
        'IAEA-Therapeutic',
        'IBA-Eval-2007',
        'IBA-Eval',
        'INDEN-Aug2023',
        'INDEN-Feb2022',
        'INDEN.0-beta',
        'INDL-TSL',
        'IRDF-2002',
        'IRDFF-II-aux',
        'IRDFF-II-b1',
        'IRDFF-II',
        'IRDFF-v0',
        'IRDFF-v1.01',
        'IRDFF-v1.03',
        'IRDFF-v1.05',
        'IRDFF',
        'JEF-2.2',
        'JEFF-3.1.1',
        'JEFF-3.1.2',
        'JEFF-3.1',
        'JEFF-3.2',
        'JEFF-3.3-DPA',
        'JEFF-3.3',
        'JENDL-3.2',
        'JENDL-3.3',
        'JENDL-4.0-HE',
        'JENDL-4.0',
        'JENDL-4.0u2-20160106',
        'JENDL-5-Aug2023',
        'JENDL-5',
        'JENDL-AD-2017',
        'JENDL-DEU-2020',
        'JENDL-HE-2007',
        'JENDL-ImPACT-18',
        'JENDL-PD-2016.1',
        'JENDL-PD-2016',
        'MINKS-ACT',
        'PADF-2007',
        'ROSFOND-2010',
        'ROSFOND',
        'TENDL-2008',
        'TENDL-2009',
        'TENDL-2010',
        'TENDL-2011',
        'TENDL-2012',
        'TENDL-2014',
        'TENDL-2015',
        'TENDL-2017',
        'TENDL-2019',
        'TENDL-2021',
        'TENDL-2023',
        'UKDD-12']

