"""Tests for the endf6 module."""

import tempfile
from pathlib import Path

import pytest

from ndmanager.endf6 import Endf6, get_endf6, list_endf6
from ndmanager.env import NDMANAGER_ENDF6


class TestEndf6Init:
    """Test the Endf6.__init__ method."""

    def test_basic_endf6_file(self):
        """Test creating an Endf6 object from a basic neutron file."""
        # Create a minimal ENDF6 file for testing (neutron sublibrary, NSUB=10)
        # ENDF6 format uses fixed 80-character lines
        content = """                                                                          0 0  0    0
 9.223500+4 2.330248+2          0          0          0          09228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf6", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            endf6 = Endf6(temp_path)
            assert endf6.filename == temp_path
            assert endf6.nuclide.Z == 92
            assert endf6.nuclide.A == 235
            assert endf6.nuclide.M == 0
            assert endf6.sublibrary == "n"
        finally:
            Path(temp_path).unlink()

    def test_photo_sublibrary(self):
        """Test creating an Endf6 object from a photo sublibrary file."""
        # NSUB=3 for photo
        content = """                                                                          0 0  0    0
 9.223500+4 2.330248+2          0          0          0          09228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 2.000000+7          0          0          3          8 125 1451    3
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf6", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            endf6 = Endf6(temp_path)
            assert endf6.sublibrary == "photo"
        finally:
            Path(temp_path).unlink()

    def test_decay_sublibrary(self):
        """Test creating an Endf6 object from a decay sublibrary file."""
        # NSUB=4 for decay
        content = """                                                                          0 0  0    0
 9.522400+4 2.410000+2          0          0          0          09528 1451    1
 0.000000+0 0.000000+0          0          0          0          69528 1451    2
 1.000000+0 2.000000+7          0          0          4          8 125 1451    3
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf6", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            endf6 = Endf6(temp_path)
            assert endf6.sublibrary == "decay"
        finally:
            Path(temp_path).unlink()

    def test_path_object(self):
        """Test that Endf6 accepts a Path object."""
        content = """                                                                          0 0  0    0
 9.223500+4 2.330248+2          0          0          0          09228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".endf6", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            endf6 = Endf6(temp_path)
            assert endf6.nuclide.Z == 92
            assert endf6.sublibrary == "n"
        finally:
            temp_path.unlink()


class TestGetEndf6:
    """Test the get_endf6 function."""

    def test_get_existing_file_without_extension(self):
        """Test getting an ENDF6 file without specifying the extension."""
        result = get_endf6("foo", "n", "H1")
        assert result.exists()
        assert result.suffix == ".endf6"
        assert result.name == "H1.endf6"

    def test_get_existing_file_with_extension(self):
        """Test getting an ENDF6 file with the extension specified."""
        result = get_endf6("foo", "n", "H1.endf6")
        assert result.exists()
        assert result.suffix == ".endf6"

    def test_nonexistent_library(self):
        """Test that ValueError is raised for nonexistent library."""
        with pytest.raises(ValueError, match="Library 'nonexistent' does not exist"):
            get_endf6("nonexistent", "n", "H1")

    def test_nonexistent_sublibrary(self):
        """Test that ValueError is raised for nonexistent sublibrary."""
        with pytest.raises(ValueError, match="No nonexistent sublibrary available"):
            get_endf6("foo", "nonexistent", "H1")

    def test_nonexistent_nuclide(self):
        """Test that ValueError is raised for nonexistent nuclide."""
        with pytest.raises(ValueError, match="No Pu999 nuclide available"):
            get_endf6("foo", "n", "Pu999")


class TestListEndf6:
    """Test the list_endf6 function."""

    def test_basic_listing(self):
        """Test listing ENDF6 files from a base library."""
        params = {"base": "foo"}
        result = list_endf6("n", params)
        
        assert isinstance(result, dict)
        # Should have at least one entry (H1)
        assert len(result) > 0
        # All values should be Path objects
        for path in result.values():
            assert isinstance(path, Path)
            assert path.suffix == ".endf6"

    def test_omit_nuclides(self):
        """Test omitting specific nuclides from the listing."""
        params = {"base": "foo", "omit": "H1"}
        result = list_endf6("n", params)
        
        # H1 should not be in the result
        assert "H1" not in result

    def test_omit_multiple_nuclides(self):
        """Test omitting multiple nuclides."""
        # First get the full list
        params_full = {"base": "foo"}
        result_full = list_endf6("n", params_full)
        
        # Get two nuclide names to omit (if available)
        nuclides_to_omit = list(result_full.keys())[:2]
        
        omit_str = " ".join(nuclides_to_omit)
        params = {"base": "foo", "omit": omit_str}
        result = list_endf6("n", params)
        
        # Omitted nuclides should not be in the result
        for nuclide in nuclides_to_omit:
            assert nuclide not in result

    def test_neutron_removal(self):
        """Test that neutron evaluations (n1, nn1, N1) are automatically removed."""
        # Create a temporary directory structure with neutron files
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            sublibrary_dir = base_dir / "testlib" / "n"
            sublibrary_dir.mkdir(parents=True)
            
            # Create neutron files and a regular file
            neutron_content = """                                                                          0 0  0    0
 1.000000+0 1.000000+0          0          0          0          0   1 1451    1
 0.000000+0 0.000000+0          0          0          0          6   1 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            regular_content = """                                                                          0 0  0    0
 1.001000+3 1.000000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            
            (sublibrary_dir / "n1.endf6").write_text(neutron_content)
            (sublibrary_dir / "nn1.endf6").write_text(neutron_content)
            (sublibrary_dir / "N1.endf6").write_text(neutron_content)
            (sublibrary_dir / "H1.endf6").write_text(regular_content)
            
            # Mock the NDMANAGER_ENDF6 path
            import ndmanager.endf6
            original_path = ndmanager.endf6.NDMANAGER_ENDF6
            try:
                ndmanager.endf6.NDMANAGER_ENDF6 = base_dir
                
                params = {"base": "testlib"}
                result = list_endf6("n", params)
                
                # Neutron files should be removed
                assert "n1" not in result
                assert "nn1" not in result
                assert "N1" not in result
                # Regular file should remain
                assert "H1" in result
            finally:
                ndmanager.endf6.NDMANAGER_ENDF6 = original_path

    def test_add_guest_library(self):
        """Test adding nuclides from a guest library."""
        # Create a temporary directory structure with base and guest libraries
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create base library
            base_sublibrary = base_dir / "baselib" / "n"
            base_sublibrary.mkdir(parents=True)
            
            base_content = """                                                                          0 0  0    0
 1.001000+3 1.000000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (base_sublibrary / "H1.endf6").write_text(base_content)
            
            # Create guest library
            guest_sublibrary = base_dir / "guestlib" / "n"
            guest_sublibrary.mkdir(parents=True)
            
            guest_content = """                                                                          0 0  0    0
 2.004000+3 3.968000+0          0          0          0          0 228 1451    1
 0.000000+0 0.000000+0          0          0          0          6 228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (guest_sublibrary / "He4.endf6").write_text(guest_content)
            
            # Mock the NDMANAGER_ENDF6 path
            import ndmanager.endf6
            original_path = ndmanager.endf6.NDMANAGER_ENDF6
            try:
                ndmanager.endf6.NDMANAGER_ENDF6 = base_dir
                
                params = {"base": "baselib", "add": {"guestlib": "He4"}}
                result = list_endf6("n", params)
                
                # Both H1 and He4 should be present
                assert "H1" in result
                assert "He4" in result
                assert result["H1"].parent.parent.name == "baselib"
                assert result["He4"].parent.parent.name == "guestlib"
            finally:
                ndmanager.endf6.NDMANAGER_ENDF6 = original_path

    def test_add_overwrites_base(self):
        """Test that guest library nuclides overwrite base library nuclides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create base library with H1
            base_sublibrary = base_dir / "baselib" / "n"
            base_sublibrary.mkdir(parents=True)
            base_content = """                                                                          0 0  0    0
 1.001000+3 1.000000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (base_sublibrary / "H1.endf6").write_text(base_content)
            
            # Create guest library with H1
            guest_sublibrary = base_dir / "guestlib" / "n"
            guest_sublibrary.mkdir(parents=True)
            guest_content = """                                                                          0 0  0    0
 1.001000+3 1.008000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (guest_sublibrary / "H1.endf6").write_text(guest_content)
            
            import ndmanager.endf6
            original_path = ndmanager.endf6.NDMANAGER_ENDF6
            try:
                ndmanager.endf6.NDMANAGER_ENDF6 = base_dir
                
                params = {"base": "baselib", "add": {"guestlib": "H1"}}
                result = list_endf6("n", params)
                
                # H1 should come from guest library
                assert "H1" in result
                assert result["H1"].parent.parent.name == "guestlib"
            finally:
                ndmanager.endf6.NDMANAGER_ENDF6 = original_path

    def test_add_multiple_nuclides_from_guest(self):
        """Test adding multiple nuclides from a guest library."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            base_sublibrary = base_dir / "baselib" / "n"
            base_sublibrary.mkdir(parents=True)
            h1_content = """                                                                          0 0  0    0
 1.001000+3 1.000000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (base_sublibrary / "H1.endf6").write_text(h1_content)
            
            guest_sublibrary = base_dir / "guestlib" / "n"
            guest_sublibrary.mkdir(parents=True)
            he4_content = """                                                                          0 0  0    0
 2.004000+3 3.968000+0          0          0          0          0 228 1451    1
 0.000000+0 0.000000+0          0          0          0          6 228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            li6_content = """                                                                          0 0  0    0
 3.006000+3 6.015000+0          0          0          0          0 325 1451    1
 0.000000+0 0.000000+0          0          0          0          6 325 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""
            (guest_sublibrary / "He4.endf6").write_text(he4_content)
            (guest_sublibrary / "Li6.endf6").write_text(li6_content)
            
            import ndmanager.endf6
            original_path = ndmanager.endf6.NDMANAGER_ENDF6
            try:
                ndmanager.endf6.NDMANAGER_ENDF6 = base_dir
                
                params = {"base": "baselib", "add": {"guestlib": "He4 Li6"}}
                result = list_endf6("n", params)
                
                assert "H1" in result
                assert "He4" in result
                assert "Li6" in result
            finally:
                ndmanager.endf6.NDMANAGER_ENDF6 = original_path

    def test_add_nonexistent_nuclide_raises_error(self):
        """Test that adding a nonexistent nuclide from guest library raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            base_sublibrary = base_dir / "baselib" / "n"
            base_sublibrary.mkdir(parents=True)
            
            guest_sublibrary = base_dir / "guestlib" / "n"
            guest_sublibrary.mkdir(parents=True)
            
            import ndmanager.endf6
            original_path = ndmanager.endf6.NDMANAGER_ENDF6
            try:
                ndmanager.endf6.NDMANAGER_ENDF6 = base_dir
                
                params = {"base": "baselib", "add": {"guestlib": "Nonexistent999"}}
                
                with pytest.raises(ValueError, match="Nuclide Nonexistent999 is not available"):
                    list_endf6("n", params)
            finally:
                ndmanager.endf6.NDMANAGER_ENDF6 = original_path

    def test_photo_sublibrary(self):
        """Test listing files from photo sublibrary."""
        params = {"base": "foo"}
        result = list_endf6("photo", params)
        
        assert isinstance(result, dict)
        for path in result.values():
            assert path.suffix == ".endf6"

    def test_empty_params(self):
        """Test that only required 'base' parameter works."""
        params = {"base": "foo"}
        result = list_endf6("n", params)
        
        assert isinstance(result, dict)
        assert len(result) > 0
