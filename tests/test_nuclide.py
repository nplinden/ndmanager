"""Tests for the Nuclide class."""

import tempfile
from pathlib import Path

import pytest

from ndmanager.nuclide import Nuclide


class TestNuclideInit:
    """Test the __init__ method."""

    def test_basic_nuclide(self):
        """Test creating a basic nuclide."""
        nuclide = Nuclide(92, 235, 0)
        assert nuclide.Z == 92
        assert nuclide.A == 235
        assert nuclide.M == 0
        assert nuclide.element == "U"

    def test_metastable_nuclide(self):
        """Test creating a metastable nuclide."""
        nuclide = Nuclide(95, 242, 1)
        assert nuclide.Z == 95
        assert nuclide.A == 242
        assert nuclide.M == 1
        assert nuclide.element == "Am"

    def test_element_only(self):
        """Test creating a nuclide for an element only."""
        nuclide = Nuclide(6, None, None)
        assert nuclide.Z == 6
        assert nuclide.A is None
        assert nuclide.M is None
        assert nuclide.element == "C"


class TestFromName:
    """Test the from_name classmethod."""

    def test_basic_nuclide_name(self):
        """Test parsing a basic nuclide name."""
        nuclide = Nuclide.from_name("U235")
        assert nuclide.Z == 92
        assert nuclide.A == 235
        assert nuclide.M == 0

    def test_metastable_nuclide_name(self):
        """Test parsing a metastable nuclide name."""
        nuclide = Nuclide.from_name("Am242_m1")
        assert nuclide.Z == 95
        assert nuclide.A == 242
        assert nuclide.M == 1

    def test_second_metastable_state(self):
        """Test parsing a second metastable state."""
        nuclide = Nuclide.from_name("Tc99_m2")
        assert nuclide.Z == 43
        assert nuclide.A == 99
        assert nuclide.M == 2

    def test_element_only_name(self):
        """Test parsing an element name."""
        nuclide = Nuclide.from_name("C")
        assert nuclide.Z == 6
        assert nuclide.A is None
        assert nuclide.M is None

    def test_various_elements(self):
        """Test parsing various element names."""
        test_cases = [
            ("H1", 1, 1, 0),
            ("He4", 2, 4, 0),
            ("Fe56", 26, 56, 0),
            ("Pu239", 94, 239, 0),
            ("Cd115_m1", 48, 115, 1),
        ]
        for name, expected_z, expected_a, expected_m in test_cases:
            nuclide = Nuclide.from_name(name)
            assert nuclide.Z == expected_z
            assert nuclide.A == expected_a
            assert nuclide.M == expected_m


class TestFromZam:
    """Test the from_zam classmethod."""

    def test_basic_zam(self):
        """Test parsing a basic ZAM number."""
        nuclide = Nuclide.from_zam(922350)
        assert nuclide.Z == 92
        assert nuclide.A == 235
        assert nuclide.M == 0

    def test_metastable_zam(self):
        """Test parsing a metastable ZAM number."""
        nuclide = Nuclide.from_zam(952421)
        assert nuclide.Z == 95
        assert nuclide.A == 242
        assert nuclide.M == 1

    def test_second_metastable_zam(self):
        """Test parsing a second metastable state ZAM."""
        nuclide = Nuclide.from_zam(430992)
        assert nuclide.Z == 43
        assert nuclide.A == 99
        assert nuclide.M == 2

    def test_element_only_zam(self):
        """Test parsing an element-only ZAM."""
        nuclide = Nuclide.from_zam(60000)
        assert nuclide.Z == 6
        assert nuclide.A == 0
        assert nuclide.M == 0

    def test_various_zams(self):
        """Test parsing various ZAM numbers."""
        test_cases = [
            (10010, 1, 1, 0),  # H-1
            (20040, 2, 4, 0),  # He-4
            (260560, 26, 56, 0),  # Fe-56
            (942390, 94, 239, 0),  # Pu-239
            (481151, 48, 115, 1),  # Cd-115m
        ]
        for zam, expected_z, expected_a, expected_m in test_cases:
            nuclide = Nuclide.from_zam(zam)
            assert nuclide.Z == expected_z
            assert nuclide.A == expected_a
            assert nuclide.M == expected_m


class TestFromIaeaName:
    """Test the from_iaea_name classmethod."""

    def test_basic_iaea_name(self):
        """Test parsing a basic IAEA name."""
        nuclide = Nuclide.from_iaea_name("092-U-235")
        assert nuclide.Z == 92
        assert nuclide.A == 235
        assert nuclide.M == 0

    def test_metastable_iaea_name(self):
        """Test parsing a metastable IAEA name."""
        nuclide = Nuclide.from_iaea_name("048-Cd-115M")
        assert nuclide.Z == 48
        assert nuclide.A == 115
        assert nuclide.M == 1

    def test_second_metastable_iaea_name(self):
        """Test parsing a second metastable state IAEA name."""
        nuclide = Nuclide.from_iaea_name("043-Tc-99N")
        assert nuclide.Z == 43
        assert nuclide.A == 99
        assert nuclide.M == 2

    def test_various_iaea_names(self):
        """Test parsing various IAEA names."""
        test_cases = [
            ("001-H-1", 1, 1, 0),
            ("002-He-4", 2, 4, 0),
            ("026-Fe-56", 26, 56, 0),
            ("094-Pu-239", 94, 239, 0),
        ]
        for name, expected_z, expected_a, expected_m in test_cases:
            nuclide = Nuclide.from_iaea_name(name)
            assert nuclide.Z == expected_z
            assert nuclide.A == expected_a
            assert nuclide.M == expected_m


class TestFromFile:
    """Test the from_file classmethod."""

    def test_basic_endf6_file(self):
        """Test parsing a basic ENDF6 file."""
        # Create a minimal ENDF6 file for testing
        content = """Retrieved by E4-util: 2018/02/07,18:09:00                            1 0  0    0
 9.223500+4 2.330248+2          1          1          0          19228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 3.000000+7          0          0         10          89228 1451    3
 0.000000+0 0.000000+0          0          0        656        4239228 1451    4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            nuclide = Nuclide.from_file(temp_path)
            assert nuclide.Z == 92
            assert nuclide.A == 235
            assert nuclide.M == 0
        finally:
            Path(temp_path).unlink()

    def test_metastable_endf6_file(self):
        """Test parsing a metastable nuclide from ENDF6 file."""
        content = """Retrieved by E4-util: 2018/02/07,18:09:49                            1 0  0    0
 9.524200+4 2.399801+2          1          1          0          19547 1451    1
 4.860000+4 0.000000+0          2          1          0          69547 1451    2
 1.000000+0 2.000000+7          0          0         10          89547 1451    3
 0.000000+0 0.000000+0          0          0        153         929547 1451    4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            nuclide = Nuclide.from_file(temp_path)
            assert nuclide.Z == 95
            assert nuclide.A == 242
            assert nuclide.M == 1
        finally:
            Path(temp_path).unlink()

    def test_element_only_endf6_file(self):
        """Test parsing an element-only ENDF6 file with NSUB=3."""
        content = """Retrieved by E4-util: 2018/02/07,17:58:30                            1 0  0    0
 92000.0000 235.984000         -1          0          0          39200 1451    1
 0.0        0.0                 0          0          0          69200 1451    2
 0.0        1.0000E+11          0          0          3          89200 1451    3
 0.0        0.0                 0          0        175         419200 1451    4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            nuclide = Nuclide.from_file(temp_path)
            assert nuclide.Z == 92
            assert nuclide.A is None
            assert nuclide.M is None
        finally:
            Path(temp_path).unlink()


class TestNameProperty:
    """Test the name property."""

    def test_basic_nuclide_name_property(self):
        """Test the name property for a basic nuclide."""
        nuclide = Nuclide(92, 235, 0)
        assert nuclide.name == "U235"

    def test_metastable_nuclide_name_property(self):
        """Test the name property for a metastable nuclide."""
        nuclide = Nuclide(95, 242, 1)
        assert nuclide.name == "Am242_m1"

    def test_second_metastable_name_property(self):
        """Test the name property for a second metastable state."""
        nuclide = Nuclide(43, 99, 2)
        assert nuclide.name == "Tc99_m2"

    def test_element_only_name_property(self):
        """Test the name property for an element only."""
        nuclide = Nuclide(6, None, None)
        assert nuclide.name == "C"

    def test_various_name_properties(self):
        """Test the name property for various nuclides."""
        test_cases = [
            (1, 1, 0, "H1"),
            (2, 4, 0, "He4"),
            (26, 56, 0, "Fe56"),
            (94, 239, 0, "Pu239"),
            (48, 115, 1, "Cd115_m1"),
        ]
        for z, a, m, expected_name in test_cases:
            nuclide = Nuclide(z, a, m)
            assert nuclide.name == expected_name


class TestZamProperty:
    """Test the zam property."""

    def test_basic_nuclide_zam_property(self):
        """Test the zam property for a basic nuclide."""
        nuclide = Nuclide(92, 235, 0)
        assert nuclide.zam == 922350

    def test_metastable_nuclide_zam_property(self):
        """Test the zam property for a metastable nuclide."""
        nuclide = Nuclide(95, 242, 1)
        assert nuclide.zam == 952421

    def test_second_metastable_zam_property(self):
        """Test the zam property for a second metastable state."""
        nuclide = Nuclide(43, 99, 2)
        assert nuclide.zam == 430992

    def test_element_only_zam_property(self):
        """Test the zam property for an element only."""
        nuclide = Nuclide(6, None, None)
        assert nuclide.zam == 60000

    def test_various_zam_properties(self):
        """Test the zam property for various nuclides."""
        test_cases = [
            (1, 1, 0, 10010),
            (2, 4, 0, 20040),
            (26, 56, 0, 260560),
            (94, 239, 0, 942390),
            (48, 115, 1, 481151),
        ]
        for z, a, m, expected_zam in test_cases:
            nuclide = Nuclide(z, a, m)
            assert nuclide.zam == expected_zam


class TestRoundTrip:
    """Test round-trip conversions between different formats."""

    def test_name_to_zam_roundtrip(self):
        """Test converting from name to ZAM and back."""
        original_name = "U235"
        nuclide = Nuclide.from_name(original_name)
        zam = nuclide.zam
        nuclide2 = Nuclide.from_zam(zam)
        assert nuclide2.name == original_name

    def test_zam_to_name_roundtrip(self):
        """Test converting from ZAM to name and back."""
        original_zam = 922350
        nuclide = Nuclide.from_zam(original_zam)
        name = nuclide.name
        nuclide2 = Nuclide.from_name(name)
        assert nuclide2.zam == original_zam

    def test_metastable_roundtrip(self):
        """Test round-trip for metastable nuclides."""
        original_name = "Am242_m1"
        nuclide = Nuclide.from_name(original_name)
        zam = nuclide.zam
        nuclide2 = Nuclide.from_zam(zam)
        assert nuclide2.name == original_name
        assert nuclide2.zam == zam

    def test_iaea_to_gnds_conversion(self):
        """Test converting from IAEA format to GNDS format."""
        iaea_name = "048-Cd-115M"
        nuclide = Nuclide.from_iaea_name(iaea_name)
        assert nuclide.name == "Cd115_m1"
        assert nuclide.zam == 481151


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_neutron(self):
        """Test neutron (Z=0)."""
        nuclide = Nuclide.from_name("n")
        assert nuclide.Z == 0
        assert nuclide.element == "n"

    def test_deuterium(self):
        """Test deuterium."""
        nuclide = Nuclide.from_name("H2")
        assert nuclide.Z == 1
        assert nuclide.A == 2
        assert nuclide.M == 0
        assert nuclide.name == "H2"

    def test_tritium(self):
        """Test tritium."""
        nuclide = Nuclide.from_name("H3")
        assert nuclide.Z == 1
        assert nuclide.A == 3
        assert nuclide.M == 0
        assert nuclide.name == "H3"

    def test_high_z_element(self):
        """Test high-Z elements."""
        nuclide = Nuclide.from_name("Og294")
        assert nuclide.Z == 118
        assert nuclide.A == 294
        assert nuclide.element == "Og"
