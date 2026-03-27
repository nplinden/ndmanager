"""Tests for the merge module."""

import shutil
import tempfile
from pathlib import Path

import h5py
import pytest

from ndmanager.merge import get_available_temperature, merge_neutron_file

# Path to test data
TEST_DATA_DIR = Path(__file__).parent / "data" / "hdf5"


def _read_temperatures(filepath: Path) -> set[int]:
    """Read temperature keys directly from HDF5, bypassing get_available_temperature."""
    with h5py.File(filepath, "r") as f:
        nuclide = next(iter(f.keys()))
        return {int(k[:-1]) for k in f[f"{nuclide}/energy"].keys()}


class TestMergeNeutronFile:
    """Test the merge_neutron_file function."""

    def test_successful_merge_different_temperatures(self):
        """Test successful merge of H1 files with different temperatures.

        The post-merge target should contain the union of both files' temperatures.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            source_path = TEST_DATA_DIR / "bar" / "neutron" / "H1.h5"

            source_temps = get_available_temperature(source_path)
            target_temps = get_available_temperature(target_path)
            expected_temps = source_temps | target_temps

            merge_neutron_file(str(source_path), str(target_path))

            final_temps = get_available_temperature(target_path)
            assert final_temps == expected_temps

            # Verify the HDF5 structure is intact for all expected temperatures
            with h5py.File(target_path, "r") as f:
                nuclide = next(iter(f.keys()))
                assert nuclide in f
                for t in expected_temps:
                    assert f"{t}K" in f[f"{nuclide}/energy"]

    def test_merge_no_new_temperatures(self):
        """Test merge when files have same temperatures - nothing should be added."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"

            initial_temps = get_available_temperature(target_path)

            merge_neutron_file(str(source_path), str(target_path))

            final_temps = get_available_temperature(target_path)
            assert final_temps == initial_temps

    def test_source_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when source has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            source_path = tmpdir_path / "source.h5"
            with h5py.File(source_path, "w") as f:
                f.create_group("H1")
                f.create_group("H2")

            target_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"

            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                merge_neutron_file(str(source_path), str(target_path))

    def test_target_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when target has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"

            target_path = tmpdir_path / "target.h5"
            with h5py.File(target_path, "w") as f:
                f.create_group("H1")
                f.create_group("H2")

            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                merge_neutron_file(str(source_path), str(target_path))

    def test_different_nuclides_raises_error(self):
        """Test that ValueError is raised when files have different nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H2.h5", target_path)
            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"

            with pytest.raises(ValueError, match="must contain data for the same nuclide"):
                merge_neutron_file(str(source_path), str(target_path))

    def test_merge_with_bar_to_foo(self):
        """Test merging bar's H1 into foo's H1.

        This tests the realistic scenario of merging data from different libraries.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            source_path = TEST_DATA_DIR / "bar" / "neutron" / "H1.h5"

            source_temps = get_available_temperature(source_path)
            target_temps = get_available_temperature(target_path)

            merge_neutron_file(str(source_path), str(target_path))

            with h5py.File(target_path, "r") as f:
                nuclide = next(iter(f.keys()))
                result_temps = {int(k[:-1]) for k in f[f"{nuclide}/energy"].keys()}
                assert result_temps == source_temps | target_temps


class TestGetAvailableTemperature:
    """Test the get_available_temperature function."""

    @pytest.mark.parametrize("library,nuclide", [
        ("foo", "H1"),
        ("foo", "H2"),
        ("bar", "H1"),
        ("bar", "H2"),
    ])
    def test_temperatures_match_hdf5_keys(self, library, nuclide):
        """Test that returned temperatures match the energy keys in the HDF5 file."""
        filepath = TEST_DATA_DIR / library / "neutron" / f"{nuclide}.h5"
        expected = _read_temperatures(filepath)
        assert get_available_temperature(filepath) == expected

    def test_returns_set(self):
        """Test that function returns a set."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
        assert isinstance(get_available_temperature(filepath), set)

    def test_temperature_values_are_integers(self):
        """Test that temperature values are integers."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
        assert all(isinstance(t, int) for t in get_available_temperature(filepath))

    def test_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when file has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.h5"

            with h5py.File(filepath, "w") as f:
                h1 = f.create_group("H1")
                h1.create_group("energy").create_dataset("300K", data=[1.0, 2.0])
                h2 = f.create_group("H2")
                h2.create_group("energy").create_dataset("300K", data=[1.0, 2.0])

            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                get_available_temperature(filepath)

    def test_empty_file_raises_error(self):
        """Test with an empty HDF5 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.h5"

            with h5py.File(filepath, "w") as f:
                pass

            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                get_available_temperature(filepath)
