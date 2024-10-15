import pytest
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from ndmanager.API.iaea.sublibrary import IAEASublibrary
from ndmanager.API.sha1 import compute_file_sha1



@pytest.fixture(scope="function")
def sublibrary():
    return IAEASublibrary.from_website(
        "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/",
        "d-index.htm",
        "d"
        )

def test_from_website(sublibrary):
    assert sublibrary.kind == "d"
    assert sublibrary.library_root == "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/"
    assert sublibrary.lib == "IAEA-Medical"
    assert sublibrary.library == "IAEA-Medical Charged-particle cross section database for medical radioisotope production, 2001"
    assert sublibrary.nsub == 10020
    assert sublibrary.sublibrary == "Incident-Deuteron Data"
    for key, val in sublibrary.urls.items():
        assert isinstance(key, str)
        assert isinstance(val, str)

def test_getitem(sublibrary):
    assert sublibrary["N14"] == "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/d/d_0725_7-N-14.zip"

def test_setitem(sublibrary):
    sublibrary["N15"] = sublibrary["N14"]
    sublibrary["N15"] == sublibrary.urls["N15"]

def test_len(sublibrary):
    assert len(sublibrary) == len(sublibrary.urls)

def test_keys(sublibrary):
    assert sublibrary.keys() == list(sublibrary.urls.keys())

def test_parse_index():
    url = "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/d-index.htm"
    r = requests.get(url, timeout=600)
    html = BeautifulSoup(r.text, "html.parser")
    index = html.find_all("pre")[0].text.split("\n")

    kwargs = {}
    materials = IAEASublibrary.parse_index(index, kwargs)

    assert kwargs["lib"] == 'IAEA-Medical'
    assert kwargs["library"] == 'IAEA-Medical Charged-particle cross section database for medical radioisotope production, 2001'
    assert kwargs["nsub"] == 10020
    assert kwargs["sublibrary"] == 'Incident-Deuteron Data'
    assert materials == ['7-N-14', '10-NE-0', '13-AL-27', '22-TI-0', '26-FE-0', '28-NI-0']

def test_insert_separator():
    s = "12345"
    s = IAEASublibrary.insert_separator(s, 2)
    assert s == "12$345"

def test_fetch_tape(sublibrary):
    tape = sublibrary.fetch_tape("N14")
    p = "pytest-artifacts/test_fetch_tape.endf6"
    with open(p, "w") as f:
        print(tape, file=f, end="")
    sha1 = compute_file_sha1(p)
    assert sha1 == "819e80d471cae606106d28723722bd07e5af2a2d"

def test_download_single(sublibrary):
    p = "pytest-artifacts/test_download_single.endf6"
    sublibrary.download_single("N14", p)
    sha1 = compute_file_sha1(p)
    assert sha1 == "819e80d471cae606106d28723722bd07e5af2a2d"

def test_download(sublibrary):
    target = Path("pytest-artifacts/IAEA-Medical")
    sublibrary.download(target,
               "nuclide",
               1)

    sha1 = compute_file_sha1(target / "Al27.endf6")
    assert sha1 == "e086848a085222bf49865301052e453f9d45faaf"
    sha1 = compute_file_sha1(target / "Fe0.endf6")
    assert sha1 == "6deb6a698128458d2016f8fe895ef7f6dc65ddf1"
    sha1 = compute_file_sha1(target / "N14.endf6")
    assert sha1 == "819e80d471cae606106d28723722bd07e5af2a2d"
    sha1 = compute_file_sha1(target / "Ne0.endf6")
    assert sha1 == "0ea2c387aa50b45539a32da43dc088d3f27aa558"
    sha1 = compute_file_sha1(target / "Ni0.endf6")
    assert sha1 == "1219aa9f5c858222ba0797201b7718a084f20efa"
    sha1 = compute_file_sha1(target / "Ti0.endf6")
    assert sha1 == "b7ee2459ba5b8469399e68bbbe09ab5b85217b2b"
