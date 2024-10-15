from ndmanager.API.iaea import IAEALibrary, IAEASublibrary
import pytest


def test_from_website():
    library = IAEALibrary.from_website("ENDF-B-VIII.0/")
    assert library.name == "ENDF-B-VIII.0/"
    assert library.lib == "ENDF/B-VIII.0"
    assert library.library == "ENDF/B-VIII.0 U.S. Evaluated Nuclear Data Library, issued in 2018"
    assert library.valid == True
    assert library.url == "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/"
    for sublib in library.sublibraries.values():
        assert isinstance(sublib, IAEASublibrary)

def test_get_item(iaea):
    library = iaea["endfb8"]
    for sublib in library.sublibraries:
        assert library[sublib] == library.sublibraries[sublib]

def test_set_item():
    library = IAEALibrary.from_website("ENDF-B-VIII.0/")
    library["neutron"] = library["n"]
    assert library["neutron"] == library["n"]

def test_keys(iaea):
    library = iaea["endfb8"]
    assert library.keys() == ['g',
            'photo',
            'decay',
            'sfpy',
            'ard',
            'n',
            'nfpy',
            'tsl',
            'std',
            'e',
            'p',
            'd',
            't',
            'he3',
            'he4']

def test_parse_index():
    kwargs = {
        "url": "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/",
        "sublibraries": {}
    }
    IAEALibrary.parse_index(kwargs)
    assert kwargs["url"] ==  "https://www-nds.iaea.org/public/download-endf/IAEA-Medical/"
    assert kwargs["lib"] == "IAEA-Medical"
    assert kwargs["library"] == "IAEA-Medical Charged-particle cross section database for medical radioisotope production, 2001"
    assert sorted(list(kwargs["sublibraries"].keys())) == ['d', 'he3', 'he4', 'p']
    for value in kwargs["sublibraries"].values():
        assert isinstance(value, IAEASublibrary)


