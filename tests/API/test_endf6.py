import pytest

from ndmanager.API.endf6 import Endf6
from ndmanager.API.utils import get_endf6


def test_endf6(install_test):
    for neutron in ["C12", "H1"]:
        tape = get_endf6("foo", "n", neutron)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == neutron
        assert evaluation.sublibrary == "n"

    for ard in ["C", "H"]:
        tape = get_endf6("foo", "ard", ard)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == ard
        assert evaluation.sublibrary == "ard"

    for photo in ["C", "H"]:
        tape = get_endf6("foo", "photo", photo)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == photo
        assert evaluation.sublibrary == "photo"

    tape = get_endf6("foo", "tsl", "tsl_0037_H(CH2).endf6")
    evaluation = Endf6(tape)

    assert evaluation.filename == tape
    assert evaluation.nuclide.name == "n137"  # An anomaly of TSL files
    assert evaluation.sublibrary == "tsl"
