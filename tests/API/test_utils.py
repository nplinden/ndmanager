import pytest

from ndmanager.API.utils import get_endf6, list_endf6


def test_get_endf6(install):
    get_endf6("foo", "n", "C12").samefile("pytest-artifacts/endf6/foo/n/C12.endf6")
    with pytest.raises(ValueError):
        get_endf6("coucou", "n", "C12")
    with pytest.raises(ValueError):
        get_endf6("foo", "coucou", "C12")
    with pytest.raises(ValueError):
        get_endf6("foo", "n", "coucou")


def test_list_endf6(install):
    params = {"base": "foo"}
    tapes = list_endf6("n", params)
    assert tapes["H1"].samefile("pytest-artifacts/endf6/foo/n/H1.endf6")
    assert tapes["C12"].samefile("pytest-artifacts/endf6/foo/n/C12.endf6")
    assert tapes["Am242_m1"].samefile("pytest-artifacts/endf6/foo/n/Am242_m1.endf6")

    params = {"base": "foo"}
    tapes = list_endf6("photo", params)
    assert tapes["H"].samefile("pytest-artifacts/endf6/foo/photo/H.endf6")
    assert tapes["C"].samefile("pytest-artifacts/endf6/foo/photo/C.endf6")

    params = {"base": "foo"}
    tapes = list_endf6("ard", params)
    assert tapes["H"].samefile("pytest-artifacts/endf6/foo/ard/H.endf6")
    assert tapes["C"].samefile("pytest-artifacts/endf6/foo/ard/C.endf6")

    params = {"base": "foo", "add": {"bar": "Am242_m1"}}
    tapes = list_endf6("n", params)
    assert tapes["H1"].samefile("pytest-artifacts/endf6/foo/n/H1.endf6")
    assert tapes["C12"].samefile("pytest-artifacts/endf6/foo/n/C12.endf6")
    assert tapes["Am242_m1"].samefile("pytest-artifacts/endf6/bar/n/Am242_m1.endf6")

    params = {"base": "foo", "add": {"bar": "Pu239"}}
    with pytest.raises(ValueError):
        list_endf6("n", params)
