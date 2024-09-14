import pytest

from ndmanager.API.utils import get_endf6

def test_get_endf6(install_test):
    get_endf6("test", "n", "C12").samefile("pytest-artifacts/endf6/test/n/C12.endf6")