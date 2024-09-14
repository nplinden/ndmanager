import pytest

from ndmanager.API.utils import get_endf6

def test_get_endf6(install_test):
    get_endf6("test", "n", "C12").samefile("pytest-artifacts/endf6/test/n/C12.endf6")
    with pytest.raises(ValueError):
        get_endf6("coucou", "n", "C12")
    with pytest.raises(ValueError):
        get_endf6("test", "coucou", "C12")
    with pytest.raises(ValueError):
        get_endf6("test", "n", "coucou")