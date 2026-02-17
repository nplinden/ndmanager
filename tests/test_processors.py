"""Tests for the processors module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ndmanager.processors import process_neutron, process_photon, process_tsl


class TestProcessNeutron:
    """Test the process_neutron function."""

    def test_no_temperatures_raises_error(self):
        """Test that ValueError is raised when no temperatures are specified."""
        with tempfile.NamedTemporaryFile(suffix=".tape") as tape_file:
            tape_path = Path(tape_file.name)
            target_path = Path("/tmp/target.h5")
            
            with pytest.raises(ValueError, match="No temperatures specified"):
                process_neutron(target_path, tape_path, set())

    def test_nonexistent_tape_raises_error(self):
        """Test that ValueError is raised when tape file does not exist."""
        tape_path = Path("/nonexistent/tape.file")
        target_path = Path("/tmp/target.h5")
        temperatures = {300, 600}
        
        with pytest.raises(ValueError, match="does not exist"):
            process_neutron(target_path, tape_path, temperatures)

    @patch("ndmanager.processors.IncidentNeutron")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file(self, mock_get_logger, mock_incident_neutron):
        """Test creating a new neutron HDF5 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a tape file
            tape_path = tmpdir_path / "tape.file"
            tape_path.write_text("dummy content")
            
            # Target file doesn't exist yet
            target_path = tmpdir_path / "target.h5"
            temperatures = {300, 600, 900}
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Mock IncidentNeutron
            mock_data = Mock()
            mock_incident_neutron.from_njoy.return_value = mock_data
            
            # Call the function
            result = process_neutron(target_path, tape_path, temperatures)
            
            # Verify logger calls
            assert mock_logger.info.call_count >= 2
            mock_logger.info.assert_any_call("Processing neutron data for %s", "target")
            
            # Verify IncidentNeutron.from_njoy was called with correct parameters
            mock_incident_neutron.from_njoy.assert_called_once_with(tape_path, temperatures=temperatures)
            
            # Verify export_to_hdf5 was called
            mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
            
            # Verify return value
            assert result == target_path

    @patch("ndmanager.processors.merge_neutron_file")
    @patch("ndmanager.processors.get_available_temperature")
    @patch("ndmanager.processors.IncidentNeutron")
    @patch("ndmanager.processors.get_logger")
    def test_merge_with_existing_file(
        self, mock_get_logger, mock_incident_neutron, mock_get_available_temp, mock_merge
    ):
        """Test merging new temperatures with an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a tape file
            tape_path = tmpdir_path / "tape.file"
            tape_path.write_text("dummy content")
            
            # Target file already exists
            target_path = tmpdir_path / "target.h5"
            target_path.write_text("existing hdf5 content")
            
            # Existing temperatures: 300, 600
            # New temperatures requested: 300, 600, 900
            # Should only process: 900
            existing_temps = {300, 600}
            requested_temps = {300, 600, 900}
            mock_get_available_temp.return_value = existing_temps
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Mock IncidentNeutron
            mock_data = Mock()
            mock_incident_neutron.from_njoy.return_value = mock_data
            
            # Call the function
            result = process_neutron(target_path, tape_path, requested_temps)
            
            # Verify get_available_temperature was called
            mock_get_available_temp.assert_called_once_with(target_path)
            
            # Verify IncidentNeutron.from_njoy was called with only new temperatures
            expected_new_temps = {900}
            mock_incident_neutron.from_njoy.assert_called_once_with(tape_path, expected_new_temps)
            
            # Verify export_to_hdf5 and merge were called
            mock_data.export_to_hdf5.assert_called_once()
            mock_merge.assert_called_once()
            
            assert result == target_path

    @patch("ndmanager.processors.get_available_temperature")
    @patch("ndmanager.processors.get_logger")
    def test_no_new_temperatures_needed(self, mock_get_logger, mock_get_available_temp):
        """Test when all requested temperatures already exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a tape file
            tape_path = tmpdir_path / "tape.file"
            tape_path.write_text("dummy content")
            
            # Target file already exists
            target_path = tmpdir_path / "target.h5"
            target_path.write_text("existing hdf5 content")
            
            # All requested temperatures already exist
            temperatures = {300, 600, 900}
            mock_get_available_temp.return_value = temperatures
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Call the function
            result = process_neutron(target_path, tape_path, temperatures)
            
            # Verify early return message
            mock_logger.info.assert_any_call("No new processing is necessary, exiting")
            
            # Verify return value
            assert result == target_path


class TestProcessPhoton:
    """Test the process_photon function."""

    def test_nonexistent_photo_file_raises_error(self):
        """Test that ValueError is raised when photo file does not exist."""
        photo_path = Path("/nonexistent/photo.endf6")
        target_path = Path("/tmp/target.h5")
        
        with pytest.raises(ValueError, match="Photon ENDF6 file.*does not exist"):
            process_photon(target_path, photo_path)

    def test_nonexistent_ard_file_raises_error(self):
        """Test that ValueError is raised when ARD file does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create photo file
            photo_path = tmpdir_path / "photo.endf6"
            photo_path.write_text("dummy photo content")
            
            # ARD file doesn't exist
            ard_path = Path("/nonexistent/ard.endf6")
            target_path = tmpdir_path / "target.h5"
            
            with pytest.raises(ValueError, match="Atomic relaxation data ENDF6 file.*does not exist"):
                process_photon(target_path, photo_path, ard_path)

    @patch("ndmanager.processors.IncidentPhoton")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file_without_ard(self, mock_get_logger, mock_incident_photon):
        """Test creating a new photon HDF5 file without ARD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create photo file
            photo_path = tmpdir_path / "photo.endf6"
            photo_path.write_text("dummy photo content")
            
            # Target file doesn't exist yet
            target_path = tmpdir_path / "target.h5"
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Mock IncidentPhoton
            mock_data = Mock()
            mock_incident_photon.from_endf.return_value = mock_data
            
            # Call the function
            result = process_photon(target_path, photo_path)
            
            # Verify logger calls
            assert mock_logger.info.call_count >= 2
            mock_logger.info.assert_any_call("Processing photon data for %s", "target")
            
            # Verify IncidentPhoton.from_endf was called
            mock_incident_photon.from_endf.assert_called_once_with(photo_path, None)
            
            # Verify export_to_hdf5 was called
            mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
            
            # Verify return value
            assert result == target_path

    @patch("ndmanager.processors.IncidentPhoton")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file_with_ard(self, mock_get_logger, mock_incident_photon):
        """Test creating a new photon HDF5 file with ARD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create photo and ARD files
            photo_path = tmpdir_path / "photo.endf6"
            photo_path.write_text("dummy photo content")
            ard_path = tmpdir_path / "ard.endf6"
            ard_path.write_text("dummy ard content")
            
            # Target file doesn't exist yet
            target_path = tmpdir_path / "target.h5"
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Mock IncidentPhoton
            mock_data = Mock()
            mock_incident_photon.from_endf.return_value = mock_data
            
            # Call the function
            result = process_photon(target_path, photo_path, ard_path)
            
            # Verify IncidentPhoton.from_endf was called with both files
            mock_incident_photon.from_endf.assert_called_once_with(photo_path, ard_path)
            
            # Verify export_to_hdf5 was called
            mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
            
            assert result == target_path

    @patch("ndmanager.processors.get_logger")
    def test_existing_file_skips_processing(self, mock_get_logger):
        """Test that existing files are not reprocessed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create photo file
            photo_path = tmpdir_path / "photo.endf6"
            photo_path.write_text("dummy photo content")
            
            # Target file already exists
            target_path = tmpdir_path / "target.h5"
            target_path.write_text("existing hdf5 content")
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Call the function
            result = process_photon(target_path, photo_path)
            
            # Verify logger indicates no processing
            mock_logger.info.assert_any_call(
                "Target file already exists at %s, no processing necessary", target_path
            )
            
            assert result == target_path


class TestProcessTsl:
    """Test the process_tsl function."""

    def test_nonexistent_neutron_file_raises_error(self):
        """Test that ValueError is raised when neutron file does not exist."""
        neutron_path = Path("/nonexistent/neutron.endf6")
        tsl_path = Path("/tmp/tsl.endf6")
        target_path = Path("/tmp/target.h5")
        
        with pytest.raises(ValueError, match="Neutron ENDF6 file.*does not exist"):
            process_tsl(target_path, neutron_path, tsl_path)

    def test_nonexistent_tsl_file_raises_error(self):
        """Test that ValueError is raised when TSL file does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create neutron file
            neutron_path = tmpdir_path / "neutron.endf6"
            neutron_path.write_text("dummy neutron content")
            
            # TSL file doesn't exist
            tsl_path = Path("/nonexistent/tsl.endf6")
            target_path = tmpdir_path / "target.h5"
            
            with pytest.raises(ValueError, match="TSL ENDF6 file.*does not exist"):
                process_tsl(target_path, neutron_path, tsl_path)

    @patch("ndmanager.processors.ThermalScattering")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file(self, mock_get_logger, mock_thermal_scattering):
        """Test creating a new TSL HDF5 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create neutron and TSL files
            neutron_path = tmpdir_path / "neutron.endf6"
            neutron_path.write_text("dummy neutron content")
            tsl_path = tmpdir_path / "tsl.endf6"
            tsl_path.write_text("dummy tsl content")
            
            # Target file doesn't exist yet
            target_path = tmpdir_path / "target.h5"
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Mock ThermalScattering
            mock_data = Mock()
            mock_thermal_scattering.from_njoy.return_value = mock_data
            
            # Call the function
            result = process_tsl(target_path, neutron_path, tsl_path)
            
            # Verify logger calls
            assert mock_logger.info.call_count >= 2
            mock_logger.info.assert_any_call("Processing TSL data for %s", "target")
            
            # Verify ThermalScattering.from_njoy was called
            mock_thermal_scattering.from_njoy.assert_called_once_with(neutron_path, tsl_path)
            
            # Verify export_to_hdf5 was called
            mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
            
            # Verify return value
            assert result == target_path

    @patch("ndmanager.processors.get_logger")
    def test_existing_file_skips_processing(self, mock_get_logger):
        """Test that existing files are not reprocessed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create neutron and TSL files
            neutron_path = tmpdir_path / "neutron.endf6"
            neutron_path.write_text("dummy neutron content")
            tsl_path = tmpdir_path / "tsl.endf6"
            tsl_path.write_text("dummy tsl content")
            
            # Target file already exists
            target_path = tmpdir_path / "target.h5"
            target_path.write_text("existing hdf5 content")
            
            # Mock logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Call the function
            result = process_tsl(target_path, neutron_path, tsl_path)
            
            # Verify logger indicates no processing
            mock_logger.info.assert_any_call(
                "Target file already exists at %s, no processing necessary", target_path
            )
            
            assert result == target_path


class TestLogPathCreation:
    """Test that log paths are created correctly."""

    @patch("ndmanager.processors.IncidentNeutron")
    @patch("ndmanager.processors.get_logger")
    def test_neutron_log_path(self, mock_get_logger, mock_incident_neutron):
        """Test that neutron processing creates log in correct location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            tape_path = tmpdir_path / "tape.file"
            tape_path.write_text("content")
            
            target_path = tmpdir_path / "subdir" / "target.h5"
            temperatures = {300}
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_data = Mock()
            mock_incident_neutron.from_njoy.return_value = mock_data
            
            process_neutron(target_path, tape_path, temperatures)
            
            # Verify get_logger was called with correct log path
            expected_log_path = tmpdir_path / "subdir" / "logs" / "target.log"
            mock_get_logger.assert_called_once_with(expected_log_path)

    @patch("ndmanager.processors.IncidentPhoton")
    @patch("ndmanager.processors.get_logger")
    def test_photon_log_path(self, mock_get_logger, mock_incident_photon):
        """Test that photon processing creates log in correct location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            photo_path = tmpdir_path / "photo.endf6"
            photo_path.write_text("content")
            
            target_path = tmpdir_path / "subdir" / "target.h5"
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_data = Mock()
            mock_incident_photon.from_endf.return_value = mock_data
            
            process_photon(target_path, photo_path)
            
            # Verify get_logger was called with correct log path
            expected_log_path = tmpdir_path / "subdir" / "logs" / "target.log"
            mock_get_logger.assert_called_once_with(expected_log_path)

    @patch("ndmanager.processors.ThermalScattering")
    @patch("ndmanager.processors.get_logger")
    def test_tsl_log_path(self, mock_get_logger, mock_thermal_scattering):
        """Test that TSL processing creates log in correct location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            neutron_path = tmpdir_path / "neutron.endf6"
            neutron_path.write_text("content")
            tsl_path = tmpdir_path / "tsl.endf6"
            tsl_path.write_text("content")
            
            target_path = tmpdir_path / "subdir" / "target.h5"
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_data = Mock()
            mock_thermal_scattering.from_njoy.return_value = mock_data
            
            process_tsl(target_path, neutron_path, tsl_path)
            
            # Verify get_logger was called with correct log path
            expected_log_path = tmpdir_path / "subdir" / "logs" / "target.log"
            mock_get_logger.assert_called_once_with(expected_log_path)
