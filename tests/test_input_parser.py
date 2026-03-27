"""Tests for the input_parser module."""

from pathlib import Path

import pytest

from ndmanager.input_parser import InputParser

TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def endf6_dir(monkeypatch):
    """Patch NDMANAGER_ENDF6 and NDMANAGER_HDF5 to the test data directories."""
    import ndmanager.input_parser
    monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_ENDF6", TEST_DATA_DIR / "endf6")
    monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_HDF5", TEST_DATA_DIR / "hdf5")


@pytest.fixture
def tsl_endf6_dir(tmp_path, monkeypatch):
    """Create a minimal ENDF6 directory with a jeff33-compatible TSL structure."""
    import ndmanager.input_parser

    # neutron sublibrary
    n_dir = tmp_path / "jeff33" / "n"
    n_dir.mkdir(parents=True)
    (n_dir / "H1.endf6").write_text("dummy")

    # TSL sublibrary — file name must match TSL_NEUTRON["jeff33"] key
    tsl_dir = tmp_path / "jeff33" / "tsl"
    tsl_dir.mkdir(parents=True)
    (tsl_dir / "tsl_0001_H(H2O).endf6").write_text("dummy")

    import ndmanager.endf6
    monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_ENDF6", tmp_path)
    monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_HDF5", tmp_path / "hdf5")
    monkeypatch.setattr(ndmanager.endf6, "NDMANAGER_ENDF6", tmp_path)
    return tmp_path


class TestInputParserValidation:
    """Test input validation in InputParser.__init__."""

    def test_empty_yaml_raises_error(self, tmp_path):
        """Test that an empty YAML file raises ValueError."""
        p = tmp_path / "empty.yml"
        p.write_text("")

        with pytest.raises(ValueError, match="empty or invalid"):
            InputParser(p)

    def test_invalid_yaml_raises_error(self, tmp_path):
        """Test that a YAML file with only null content raises ValueError."""
        p = tmp_path / "null.yml"
        p.write_text("~")  # YAML null

        with pytest.raises(ValueError, match="empty or invalid"):
            InputParser(p)

    def test_missing_name_raises_error(self, tmp_path):
        """Test that a YAML file without a 'name' field raises ValueError."""
        p = tmp_path / "noname.yml"
        p.write_text("summary: A library without a name\nneutron:\n  temperatures: 300\n")

        with pytest.raises(ValueError, match="missing required field 'name'"):
            InputParser(p)

    def test_valid_yaml_sets_name(self, endf6_dir, tmp_path):
        """Test that a valid YAML file with 'name' initialises correctly."""
        p = tmp_path / "mylib.yml"
        p.write_text("name: mylib\n")

        parser = InputParser(p)
        assert parser.name == "mylib"

    def test_valid_foo_yaml(self, endf6_dir):
        """Test that foo.yml parses without error and exposes expected fields."""
        parser = InputParser(TEST_DATA_DIR / "foo.yml")

        assert parser.name == "foo"
        assert parser.summary == "A simple library with H1."
        assert parser.neutron_data is not None
        assert parser.neutron_temps == {600}
        assert parser.photon_data is not None
        assert parser.tsl_data is None

    def test_tsl_without_neutron_raises_error(self, tmp_path):
        """Test that a YAML with tsl but no neutron section raises ValueError."""
        p = tmp_path / "bad.yml"
        p.write_text("name: bad\ntsl:\n  base: foo\n")

        with pytest.raises(ValueError, match="TSL section found without neutron section"):
            InputParser(p)

    def test_neutron_missing_temperatures_raises_error(self, endf6_dir, tmp_path):
        """Test that a neutron section without temperatures raises ValueError."""
        p = tmp_path / "notemp.yml"
        p.write_text("name: notemp\nneutron:\n  base: foo\n")

        with pytest.raises(ValueError, match="No temperatures found"):
            InputParser(p)

    def test_neutron_nonexistent_base_raises_error(self, endf6_dir, tmp_path):
        """Test that a neutron section with a non-existent base library raises ValueError."""
        p = tmp_path / "badbase.yml"
        p.write_text("name: badbase\nneutron:\n  temperatures: 300\n  base: nonexistent\n")

        with pytest.raises(ValueError, match="does not exist"):
            InputParser(p)


class TestListNeutrons:
    """Test the list_neutrons method."""

    def test_base_library_lists_files(self, endf6_dir, tmp_path):
        """Test that a base library lists all neutron ENDF6 files."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nneutron:\n  temperatures: 600\n  base: foo\n")

        parser = InputParser(p)
        assert "H1" in parser.neutron_data
        assert "H2" in parser.neutron_data
        for path in parser.neutron_data.values():
            assert path.suffix == ".endf6"

    def test_omit_excludes_nuclides(self, endf6_dir, tmp_path):
        """Test that omit removes specified nuclides from the result."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nneutron:\n  temperatures: 600\n  base: foo\n  omit: H1\n")

        parser = InputParser(p)
        assert "H1" not in parser.neutron_data
        assert "H2" in parser.neutron_data

    def test_multiple_temperatures(self, endf6_dir, tmp_path):
        """Test that multiple temperatures are parsed as a set."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nneutron:\n  temperatures: 300 600 900\n  base: foo\n")

        parser = InputParser(p)
        assert parser.neutron_temps == {300, 600, 900}

    def test_no_neutron_section_guard(self, endf6_dir, tmp_path):
        """Test calling list_neutrons() directly without a neutron section raises ValueError."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\n")
        parser = InputParser(p)

        with pytest.raises(ValueError, match="No neutron section found"):
            parser.list_neutrons()


class TestListPhotons:
    """Test the list_photons method."""

    def test_base_library_lists_files(self, endf6_dir, tmp_path):
        """Test that a base library lists photon files paired with ARD."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nphoton:\n  base: foo\n")

        parser = InputParser(p)
        assert "H" in parser.photon_data
        photo, ard = parser.photon_data["H"]
        assert photo.suffix == ".endf6"

    def test_add_photon_from_guest(self, endf6_dir, tmp_path):
        """Test adding photon data from a guest library via add."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nphoton:\n  add:\n    foo: H\n")

        parser = InputParser(p)
        assert "H" in parser.photon_data

    def test_nonexistent_photo_base_raises_error(self, endf6_dir, tmp_path):
        """Test that a missing photo sublibrary raises ValueError."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nphoton:\n  base: nonexistent\n")

        with pytest.raises(ValueError, match="Photon base path.*does not exist"):
            InputParser(p)

    def test_nonexistent_ard_base_raises_error(self, tmp_path, monkeypatch):
        """Test that a missing ard sublibrary raises ValueError."""
        import ndmanager.input_parser

        # Create photo dir but not ard dir
        photo_dir = tmp_path / "mylib" / "photo"
        photo_dir.mkdir(parents=True)
        monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_ENDF6", tmp_path)
        monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_HDF5", tmp_path / "hdf5")

        p = tmp_path / "lib.yml"
        p.write_text("name: lib\nphoton:\n  base: mylib\n")

        with pytest.raises(ValueError, match="ARD base path.*does not exist"):
            InputParser(p)

    def test_no_photon_section_guard(self, endf6_dir, tmp_path):
        """Test calling list_photons() directly without a photon section raises ValueError."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\n")
        parser = InputParser(p)

        with pytest.raises(ValueError, match="No photon section found"):
            parser.list_photons()


class TestListTsl:
    """Test the list_tsl method."""

    def test_base_library_lists_tsl_files(self, tsl_endf6_dir, tmp_path):
        """Test that a TSL base library lists tapes paired with neutron files."""
        p = tmp_path / "lib.yml"
        p.write_text(
            "name: lib\n"
            "neutron:\n  temperatures: 300\n  base: jeff33\n"
            "tsl:\n  base: jeff33\n"
        )

        parser = InputParser(p)
        assert "tsl_0001_H(H2O)" in parser.tsl_data

    def test_nonexistent_tsl_base_raises_error(self, tsl_endf6_dir, tmp_path):
        """Test that a missing TSL sublibrary raises ValueError."""
        p = tmp_path / "lib.yml"
        p.write_text(
            "name: lib\n"
            "neutron:\n  temperatures: 300\n  base: jeff33\n"
            "tsl:\n  base: nonexistent\n"
        )

        with pytest.raises(ValueError, match="No tsl tapes for base library"):
            InputParser(p)

    def test_unmapped_tsl_tape_raises_error(self, tmp_path, monkeypatch):
        """Test that a TSL tape with no entry in TSL_NEUTRON raises ValueError."""
        import ndmanager.input_parser

        # Create a library named "jeff33" with a TSL tape that is NOT in TSL_NEUTRON
        n_dir = tmp_path / "jeff33" / "n"
        n_dir.mkdir(parents=True)
        (n_dir / "H1.endf6").write_text("dummy")
        tsl_dir = tmp_path / "jeff33" / "tsl"
        tsl_dir.mkdir(parents=True)
        (tsl_dir / "unknown_tape.endf6").write_text("dummy")

        monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_ENDF6", tmp_path)
        monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_HDF5", tmp_path / "hdf5")

        p = tmp_path / "lib.yml"
        p.write_text(
            "name: lib\n"
            "neutron:\n  temperatures: 300\n  base: jeff33\n"
            "tsl:\n  base: jeff33\n"
        )

        with pytest.raises(ValueError, match="No nuclide mapping found"):
            InputParser(p)

    def test_omit_excludes_tsl_tapes(self, tsl_endf6_dir, tmp_path):
        """Test that omit prevents TSL tapes from being included."""
        p = tmp_path / "lib.yml"
        p.write_text(
            "name: lib\n"
            "neutron:\n  temperatures: 300\n  base: jeff33\n"
            "tsl:\n  base: jeff33\n  omit: tsl_0001_H(H2O)\n"
        )

        parser = InputParser(p)
        assert "tsl_0001_H(H2O)" not in parser.tsl_data

    def test_add_tsl_from_guest_library(self, tsl_endf6_dir, tmp_path):
        """Test adding a TSL tape from a guest library via add."""
        p = tmp_path / "lib.yml"
        p.write_text(
            "name: lib\n"
            "neutron:\n  temperatures: 300\n  base: jeff33\n"
            "tsl:\n"
            "  add:\n"
            "    jeff33:\n"
            "      tsl_0001_H(H2O): H1\n"
        )

        parser = InputParser(p)
        assert "tsl_0001_H(H2O)" in parser.tsl_data

    def test_no_tsl_section_guard(self, endf6_dir, tmp_path):
        """Test calling list_tsl() directly without a tsl section raises ValueError."""
        p = tmp_path / "lib.yml"
        p.write_text("name: lib\n")
        parser = InputParser(p)

        with pytest.raises(ValueError, match="No tsl section found"):
            parser.list_tsl()
