"""Tests for the library module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ndmanager.library import Library, sorting_key

# Path to test data
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def hdf5_dir(tmp_path, monkeypatch):
    """Patch NDMANAGER_HDF5 to a temporary directory."""
    import ndmanager.input_parser
    monkeypatch.setattr(ndmanager.input_parser, "NDMANAGER_HDF5", tmp_path)
    return tmp_path


@pytest.fixture
def foo_lib(hdf5_dir):
    """Return a Library instance built from foo.yml."""
    return Library(TEST_DATA_DIR / "foo.yml")


class TestSortingKey:
    """Test the sorting_key function."""

    def test_neutron_entry_sort_order(self):
        """Test that neutron entries get sort order 0."""
        entry = {"type": "neutron", "materials": ["U235"]}
        key = sorting_key(entry)
        assert key[0] == 0
        assert key[1] == 922350  # ZAM for U235

    def test_photon_entry_sort_order(self):
        """Test that photon entries get sort order 1."""
        entry = {"type": "photon", "materials": ["U"]}
        key = sorting_key(entry)
        assert key[0] == 1
        assert key[1] == 920000  # ZAM for U

    def test_thermal_entry_sort_order(self):
        """Test that thermal entries get sort order 2."""
        entry = {"type": "thermal", "materials": ["c_H_in_H2O"]}
        key = sorting_key(entry)
        assert key[0] == 2
        assert key[1] == "c_H_in_H2O"  # Material name as string

    def test_neutron_sorting_by_zam(self):
        """Test that neutron entries are sorted by ZAM."""
        h1_entry = {"type": "neutron", "materials": ["H1"]}
        u235_entry = {"type": "neutron", "materials": ["U235"]}
        pu239_entry = {"type": "neutron", "materials": ["Pu239"]}

        h1_key = sorting_key(h1_entry)
        u235_key = sorting_key(u235_entry)
        pu239_key = sorting_key(pu239_entry)

        # H1 < U235 < Pu239 by ZAM
        assert h1_key < u235_key < pu239_key

    def test_photon_sorting_by_zam(self):
        """Test that photon entries are sorted by ZAM."""
        h_entry = {"type": "photon", "materials": ["H"]}
        u_entry = {"type": "photon", "materials": ["U"]}

        h_key = sorting_key(h_entry)
        u_key = sorting_key(u_entry)

        # H < U by ZAM
        assert h_key < u_key

    def test_thermal_sorting_alphabetically(self):
        """Test that thermal entries are sorted alphabetically."""
        entry1 = {"type": "thermal", "materials": ["c_Al27"]}
        entry2 = {"type": "thermal", "materials": ["c_H_in_H2O"]}

        key1 = sorting_key(entry1)
        key2 = sorting_key(entry2)

        # Alphabetical: c_Al27 < c_H_in_H2O
        assert key1 < key2

    def test_sorting_precedence(self):
        """Test that neutron < photon < thermal in sort order."""
        neutron_entry = {"type": "neutron", "materials": ["U235"]}
        photon_entry = {"type": "photon", "materials": ["H"]}
        thermal_entry = {"type": "thermal", "materials": ["c_H_in_H2O"]}

        neutron_key = sorting_key(neutron_entry)
        photon_key = sorting_key(photon_entry)
        thermal_key = sorting_key(thermal_entry)

        assert neutron_key[0] < photon_key[0] < thermal_key[0]


class TestLibraryInit:
    """Test the Library.__init__ method."""

    def test_init_with_foo_yaml(self, hdf5_dir):
        """Test initialization with foo.yml test file."""
        lib = Library(TEST_DATA_DIR / "foo.yml")

        assert lib.name == "foo"
        assert lib.summary == "A simple library with H1."
        assert lib.root == hdf5_dir / "foo"
        assert lib.path == hdf5_dir / "foo" / "cross_sections.xml"
        assert lib.neutron_data is not None
        assert lib.photon_data is not None
        assert lib.neutron_temps == {600}

    def test_init_creates_root_directory(self, foo_lib):
        """Test that initialization creates root directory."""
        assert foo_lib.root.exists()
        assert foo_lib.root.is_dir()

    def test_init_with_bar_yaml(self, hdf5_dir):
        """Test initialization with bar.yml test file."""
        lib = Library(TEST_DATA_DIR / "bar.yml")

        assert lib.name == "bar"
        assert lib.neutron_temps == {500}


class TestLibraryBuild:
    """Test the Library.build method."""

    @patch.object(Library, "build_neutron")
    @patch.object(Library, "build_photon")
    @patch.object(Library, "build_tsl")
    @patch.object(Library, "sort")
    def test_build_calls_all_methods(self, mock_sort, mock_tsl, mock_photon, mock_neutron, foo_lib):
        """Test that build calls appropriate build methods."""
        foo_lib.build(jobs=1)

        # foo.yml has neutron and photon but no TSL
        mock_neutron.assert_called_once_with(1)
        mock_photon.assert_called_once_with(1)
        mock_tsl.assert_not_called()
        mock_sort.assert_called_once()

    @patch.object(Library, "build_neutron")
    @patch.object(Library, "build_photon")
    def test_build_with_jobs_parameter(self, mock_photon, mock_neutron, foo_lib):
        """Test that jobs parameter is passed to build methods."""
        foo_lib.build(jobs=4)

        mock_neutron.assert_called_once_with(4)
        mock_photon.assert_called_once_with(4)

    @patch.object(Library, "build_neutron")
    @patch.object(Library, "build_photon")
    @patch.object(Library, "build_tsl")
    @patch.object(Library, "sort")
    def test_build_calls_tsl_when_tsl_data_set(self, mock_sort, mock_tsl, mock_photon, mock_neutron, foo_lib):
        """Test that build calls build_tsl when tsl_data is set."""
        foo_lib.tsl_data = {"dummy": (Path("neutron.endf6"), Path("tsl.endf6"))}

        foo_lib.build(jobs=1)

        mock_tsl.assert_called_once_with(1)


class TestLibraryBuildNeutron:
    """Test the Library.build_neutron method."""

    @patch.object(Library, "register_file")
    @patch("ndmanager.library.process_neutron")
    def test_build_neutron_serial(self, mock_process, mock_register, foo_lib):
        """Test neutron building in serial mode (jobs=1)."""
        mock_process.return_value = None

        foo_lib.build_neutron(jobs=1)

        # Should be called for H1 and H2
        assert mock_process.call_count == 2
        assert mock_register.call_count == 2

    def test_build_neutron_invalid_jobs(self, foo_lib):
        """Test that ValueError is raised for invalid job count."""
        with pytest.raises(ValueError, match="must be at least 1"):
            foo_lib.build_neutron(jobs=0)

        with pytest.raises(ValueError, match="must be at least 1"):
            foo_lib.build_neutron(jobs=-1)

    @patch.object(Library, "register_file")
    @patch("ndmanager.library.mp")
    def test_build_neutron_parallel(self, mock_mp, mock_register, foo_lib):
        """Test neutron building in parallel mode (jobs>1)."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool

        # Simulate apply_async invoking the callback with the target path
        def invoke_callback(func, args, callback=None, error_callback=None):
            if callback:
                callback(args[0])

        mock_pool.apply_async.side_effect = invoke_callback

        foo_lib.build_neutron(jobs=4)

        # Should be called for H1 and H2
        assert mock_pool.apply_async.call_count == 2
        assert mock_register.call_count == 2
        mock_pool.close.assert_called_once()
        mock_pool.join.assert_called_once()

    @patch("ndmanager.library.mp")
    def test_build_neutron_parallel_error_callback(self, mock_mp, foo_lib):
        """Test that error_callback re-raises exceptions in parallel mode."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool

        def invoke_error_callback(func, args, callback=None, error_callback=None):
            if error_callback:
                error_callback(RuntimeError("processing failed"))

        mock_pool.apply_async.side_effect = invoke_error_callback

        with pytest.raises(RuntimeError, match="processing failed"):
            foo_lib.build_neutron(jobs=4)


class TestLibraryBuildPhoton:
    """Test the Library.build_photon method."""

    @patch.object(Library, "register_file")
    @patch("ndmanager.library.process_photon")
    def test_build_photon_serial(self, mock_process, mock_register, foo_lib):
        """Test photon building in serial mode (jobs=1)."""
        mock_process.return_value = None

        foo_lib.build_photon(jobs=1)

        # Should be called for H element
        assert mock_process.call_count == 1
        assert mock_register.call_count == 1

    def test_build_photon_invalid_jobs(self, foo_lib):
        """Test that ValueError is raised for invalid job count."""
        with pytest.raises(ValueError, match="must be at least 1"):
            foo_lib.build_photon(jobs=0)

    @patch.object(Library, "register_file")
    @patch("ndmanager.library.mp")
    def test_build_photon_parallel(self, mock_mp, mock_register, foo_lib):
        """Test photon building in parallel mode (jobs>1)."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool

        def invoke_callback(func, args, callback=None, error_callback=None):
            if callback:
                callback(args[0])

        mock_pool.apply_async.side_effect = invoke_callback

        foo_lib.build_photon(jobs=4)

        # Should be called for H element
        assert mock_pool.apply_async.call_count == 1
        assert mock_register.call_count == 1
        mock_pool.close.assert_called_once()
        mock_pool.join.assert_called_once()

    @patch("ndmanager.library.mp")
    def test_build_photon_parallel_error_callback(self, mock_mp, foo_lib):
        """Test that error_callback re-raises exceptions in parallel mode."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool

        def invoke_error_callback(func, args, callback=None, error_callback=None):
            if error_callback:
                error_callback(RuntimeError("processing failed"))

        mock_pool.apply_async.side_effect = invoke_error_callback

        with pytest.raises(RuntimeError, match="processing failed"):
            foo_lib.build_photon(jobs=4)


class TestLibraryBuildTsl:
    """Test the Library.build_tsl method."""

    def test_build_tsl_invalid_jobs(self, foo_lib):
        """Test that ValueError is raised for invalid job count."""
        # Manually set tsl_data to enable testing (foo.yml doesn't have TSL)
        foo_lib.tsl_data = {"dummy": (Path("neutron.endf6"), Path("tsl.endf6"))}

        with pytest.raises(ValueError, match="must be at least 1"):
            foo_lib.build_tsl(jobs=0)

    @patch("ndmanager.library.get_thermal_name")
    @patch("ndmanager.library.Evaluation")
    @patch.object(Library, "register_file")
    @patch("ndmanager.library.process_tsl")
    def test_build_tsl_serial(self, mock_process, mock_register, mock_eval, mock_thermal_name, foo_lib):
        """Test TSL building in serial mode (jobs=1)."""
        mock_eval.return_value.target = {"zsymam": "H(H2O)"}
        mock_thermal_name.return_value = "c_H_in_H2O"
        mock_process.return_value = None
        foo_lib.tsl_data = {"dummy": (Path("neutron.endf6"), Path("tsl.endf6"))}

        foo_lib.build_tsl(jobs=1)

        assert mock_process.call_count == 1
        assert mock_register.call_count == 1

    @patch("ndmanager.library.get_thermal_name")
    @patch("ndmanager.library.Evaluation")
    @patch.object(Library, "register_file")
    @patch("ndmanager.library.mp")
    def test_build_tsl_parallel(self, mock_mp, mock_register, mock_eval, mock_thermal_name, foo_lib):
        """Test TSL building in parallel mode (jobs>1)."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool
        mock_eval.return_value.target = {"zsymam": "H(H2O)"}
        mock_thermal_name.return_value = "c_H_in_H2O"
        foo_lib.tsl_data = {"dummy": (Path("neutron.endf6"), Path("tsl.endf6"))}

        def invoke_callback(func, args, callback=None, error_callback=None):
            if callback:
                callback(args[0])

        mock_pool.apply_async.side_effect = invoke_callback

        foo_lib.build_tsl(jobs=4)

        assert mock_pool.apply_async.call_count == 1
        assert mock_register.call_count == 1
        mock_pool.close.assert_called_once()
        mock_pool.join.assert_called_once()

    @patch("ndmanager.library.get_thermal_name")
    @patch("ndmanager.library.Evaluation")
    @patch("ndmanager.library.mp")
    def test_build_tsl_parallel_error_callback(self, mock_mp, mock_eval, mock_thermal_name, foo_lib):
        """Test that error_callback re-raises exceptions in parallel mode."""
        mock_pool = MagicMock()
        mock_mp.get_context.return_value.Pool.return_value.__enter__.return_value = mock_pool
        mock_eval.return_value.target = {"zsymam": "H(H2O)"}
        mock_thermal_name.return_value = "c_H_in_H2O"
        foo_lib.tsl_data = {"dummy": (Path("neutron.endf6"), Path("tsl.endf6"))}

        def invoke_error_callback(func, args, callback=None, error_callback=None):
            if error_callback:
                error_callback(RuntimeError("processing failed"))

        mock_pool.apply_async.side_effect = invoke_error_callback

        with pytest.raises(RuntimeError, match="processing failed"):
            foo_lib.build_tsl(jobs=4)


class TestLibraryExportToXml:
    """Test the Library.export_to_xml method."""

    @patch("ndmanager.library.DataLibrary.export_to_xml")
    def test_export_to_xml_calls_parent(self, mock_export, hdf5_dir, foo_lib):
        """Test that export_to_xml calls parent method with correct path."""
        foo_lib.export_to_xml()

        expected_path = hdf5_dir / "foo" / "cross_sections.xml"
        mock_export.assert_called_once_with(expected_path)


class TestLibraryRemove:
    """Test the Library.remove method."""

    def test_remove_deletes_directory(self, foo_lib):
        """Test that remove deletes the library directory."""
        # Create some files in the library directory
        (foo_lib.root / "test.txt").write_text("test content")
        (foo_lib.root / "subdir").mkdir()
        (foo_lib.root / "subdir" / "test2.txt").write_text("test content 2")

        assert foo_lib.root.exists()

        foo_lib.remove()

        assert not foo_lib.root.exists()

    def test_remove_nonexistent_directory(self, foo_lib):
        """Test that remove handles non-existent directory gracefully."""
        # Remove the directory manually
        foo_lib.root.rmdir()
        assert not foo_lib.root.exists()

        # Should not raise an error
        foo_lib.remove()

        assert not foo_lib.root.exists()
