import pytest

from ndmanager.API.utils import get_endf6, list_endf6


def test_get_endf6(install_test):
    get_endf6("test", "n", "C12").samefile("pytest-artifacts/endf6/test/n/C12.endf6")
    with pytest.raises(ValueError):
        get_endf6("coucou", "n", "C12")
    with pytest.raises(ValueError):
        get_endf6("test", "coucou", "C12")
    with pytest.raises(ValueError):
        get_endf6("test", "n", "coucou")


def test_list_endf6(install_test):
    params = {"basis": "test"}
    tapes = list_endf6("n", params)
    assert tapes["H1"].samefile("pytest-artifacts/endf6/test/n/H1.endf6")
    assert tapes["C12"].samefile("pytest-artifacts/endf6/test/n/C12.endf6")
    assert tapes["Am242_m1"].samefile("pytest-artifacts/endf6/test/n/Am242_m1.endf6")

    params = {"basis": "test"}
    tapes = list_endf6("photo", params)
    assert tapes["H"].samefile("pytest-artifacts/endf6/test/photo/H0.endf6")
    assert tapes["C"].samefile("pytest-artifacts/endf6/test/photo/C0.endf6")

    params = {"basis": "test"}
    tapes = list_endf6("ard", params)
    assert tapes["H"].samefile("pytest-artifacts/endf6/test/ard/H0.endf6")
    assert tapes["C"].samefile("pytest-artifacts/endf6/test/ard/C0.endf6")

    params = {"basis": "test", "add": {"test": "Am242_m1"}}
    tapes = list_endf6("n", params)
    assert tapes["H1"].samefile("pytest-artifacts/endf6/test/n/H1.endf6")
    assert tapes["C12"].samefile("pytest-artifacts/endf6/test/n/C12.endf6")
    assert tapes["Am242_m1"].samefile("pytest-artifacts/endf6/test/n/Am242_m1.endf6")

    params = {"basis": "test", "add": {"test": "Pu239"}}
    with pytest.raises(ValueError):
        list_endf6("n", params)
