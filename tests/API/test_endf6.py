import pytest

from ndmanager.API.endf6 import Endf6
from ndmanager.API.utils import get_endf6


def test_endf6(install_test):
    for neutron in ["C12", "H1"]:
        tape = get_endf6("test", "n", neutron)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == neutron
        assert evaluation.sublibrary == "n"

    for ard in ["C0", "H0"]:
        tape = get_endf6("test", "ard", ard)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == ard.rstrip("0")
        assert evaluation.sublibrary == "ard"

    for photo in ["C0", "H0"]:
        tape = get_endf6("test", "photo", photo)
        evaluation = Endf6(tape)

        assert evaluation.filename == tape
        assert evaluation.nuclide.name == photo.rstrip("0")
        assert evaluation.sublibrary == "photo"

    tape = get_endf6("test", "tsl", "tsl_0037_H(CH2).endf6")
    evaluation = Endf6(tape)

    assert evaluation.filename == tape
    assert evaluation.nuclide.name == "n137"  # An anomaly of TSL files
    assert evaluation.sublibrary == "tsl"
