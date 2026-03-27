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


class TestInputParserValidation:
    """Test input validation added to InputParser.__init__."""

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
