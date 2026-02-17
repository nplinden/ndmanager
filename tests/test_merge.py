"""Tests for the merge module."""

import shutil
import tempfile
from pathlib import Path

import h5py
import pytest

from ndmanager.merge import get_available_temperature, merge_neutron_file

# Path to test data
TEST_DATA_DIR = Path(__file__).parent / "data" / "hdf5"


class TestMergeNeutronFile:
    """Test the merge_neutron_file function."""
    
    def test_successful_merge_different_temperatures(self):
        """Test successful merge of H1 files with different temperatures.
        
        foo/H1.h5 has 0K and 600K
        bar/H1.h5 has 0K and 500K
        After merge, target should have 0K, 500K, and 600K
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Copy foo/H1.h5 as target (has 0K, 600K)
            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            
            # Use bar/H1.h5 as source (has 0K, 500K)
            source_path = TEST_DATA_DIR / "bar" / "neutron" / "H1.h5"
            
            # Get initial temperatures
            initial_temps = get_available_temperature(target_path)
            assert initial_temps == {0, 600}
            
            # Merge source into target
            merge_neutron_file(str(source_path), str(target_path))
            
            # Verify target now has all three temperatures
            final_temps = get_available_temperature(target_path)
            assert final_temps == {0, 500, 600}
            
            # Verify the structure is intact
            with h5py.File(target_path, "r") as f:
                assert "H1" in f
                assert "0K" in f["H1/energy"]
                assert "500K" in f["H1/energy"]
                assert "600K" in f["H1/energy"]
                
                # Verify reactions exist for new temperature
                assert "500K" in f["H1/reactions/reaction_002"]

    def test_merge_no_new_temperatures(self):
        """Test merge when files have same temperatures - nothing should be added."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Copy foo/H1.h5 as both source and target
            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            
            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
            
            # Get initial temperatures
            initial_temps = get_available_temperature(target_path)
            
            # Merge - should complete without error
            merge_neutron_file(str(source_path), str(target_path))
            
            # Temperatures should be unchanged
            final_temps = get_available_temperature(target_path)
            assert final_temps == initial_temps

    def test_source_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when source has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create source with multiple nuclides
            source_path = tmpdir_path / "source.h5"
            with h5py.File(source_path, "w") as f:
                f.create_group("H1")
                f.create_group("H2")
            
            # Use real target file
            target_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
            
            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                merge_neutron_file(str(source_path), str(target_path))

    def test_target_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when target has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Use real source file
            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
            
            # Create target with multiple nuclides
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
            
            # Copy H2 as target
            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H2.h5", target_path)
            
            # Use H1 as source
            source_path = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
            
            # Should raise ValueError since H1 != H2
            with pytest.raises(ValueError, match="must contain data for the same nuclide"):
                merge_neutron_file(str(source_path), str(target_path))

    def test_merge_with_bar_to_foo(self):
        """Test merging bar's H1 into foo's H1.
        
        This tests the realistic scenario of merging data from different libraries.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Copy foo/H1.h5 as target
            target_path = tmpdir_path / "target.h5"
            shutil.copy(TEST_DATA_DIR / "foo" / "neutron" / "H1.h5", target_path)
            
            # Use bar/H1.h5 as source
            source_path = TEST_DATA_DIR / "bar" / "neutron" / "H1.h5"
            
            # Merge
            merge_neutron_file(str(source_path), str(target_path))
            
            # Verify merge
            with h5py.File(target_path, "r") as f:
                temps = set(f["H1/energy"].keys())
                # Should have 0K from both, 500K from bar, 600K from foo
                assert "0K" in temps
                assert "500K" in temps
                assert "600K" in temps


class TestGetAvailableTemperature:
    """Test the get_available_temperature function."""
    
    def test_foo_h1_temperatures(self):
        """Test getting temperatures from foo/H1.h5."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
        temps = get_available_temperature(filepath)
        assert temps == {0, 600}

    def test_foo_h2_temperatures(self):
        """Test getting temperatures from foo/H2.h5."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H2.h5"
        temps = get_available_temperature(filepath)
        assert temps == {0, 600}

    def test_bar_h1_temperatures(self):
        """Test getting temperatures from bar/H1.h5."""
        filepath = TEST_DATA_DIR / "bar" / "neutron" / "H1.h5"
        temps = get_available_temperature(filepath)
        assert temps == {0, 500}

    def test_bar_h2_temperatures(self):
        """Test getting temperatures from bar/H2.h5."""
        filepath = TEST_DATA_DIR / "bar" / "neutron" / "H2.h5"
        temps = get_available_temperature(filepath)
        assert temps == {0, 500}

    def test_returns_set(self):
        """Test that function returns a set."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
        temps = get_available_temperature(filepath)
        assert isinstance(temps, set)

    def test_temperature_values_are_integers(self):
        """Test that temperature values are integers."""
        filepath = TEST_DATA_DIR / "foo" / "neutron" / "H1.h5"
        temps = get_available_temperature(filepath)
        assert all(isinstance(t, int) for t in temps)

    def test_multiple_nuclides_raises_error(self):
        """Test that ValueError is raised when file has multiple nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            filepath = tmpdir_path / "test.h5"
            
            # Create file with multiple nuclides
            with h5py.File(filepath, "w") as f:
                h1 = f.create_group("H1")
                h1_energy = h1.create_group("energy")
                h1_energy.create_dataset("300K", data=[1.0, 2.0])
                
                h2 = f.create_group("H2")
                h2_energy = h2.create_group("energy")
                h2_energy.create_dataset("300K", data=[1.0, 2.0])
            
            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                get_available_temperature(filepath)

    def test_empty_file_raises_error(self):
        """Test with an empty HDF5 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            filepath = tmpdir_path / "test.h5"
            
            # Create empty file
            with h5py.File(filepath, "w") as f:
                pass
            
            with pytest.raises(ValueError, match="must contain data for a single nuclide"):
                get_available_temperature(filepath)
