"""Tests for the processors module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ndmanager.processors import process_neutron, process_photon, process_tsl


class TestProcessNeutron:
    """Test the process_neutron function."""

    def test_no_temperatures_raises_error(self, tmp_path):
        """Test that ValueError is raised when no temperatures are specified."""
        tape_path = tmp_path / "tape.file"
        tape_path.write_text("dummy")

        with pytest.raises(ValueError, match="No temperatures specified"):
            process_neutron(tmp_path / "target.h5", tape_path, set())

    def test_nonexistent_tape_raises_error(self, tmp_path):
        """Test that ValueError is raised when tape file does not exist."""
        with pytest.raises(ValueError, match="does not exist"):
            process_neutron(tmp_path / "target.h5", tmp_path / "missing.tape", {300, 600})

    @patch("ndmanager.processors.IncidentNeutron")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file(self, mock_get_logger, mock_incident_neutron, tmp_path):
        """Test creating a new neutron HDF5 file."""
        tape_path = tmp_path / "tape.file"
        tape_path.write_text("dummy content")
        target_path = tmp_path / "target.h5"
        temperatures = {300, 600, 900}

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_data = Mock()
        mock_incident_neutron.from_njoy.return_value = mock_data

        result = process_neutron(target_path, tape_path, temperatures)

        assert mock_logger.info.call_count >= 2
        mock_logger.info.assert_any_call("Processing neutron data for %s", "target")
        mock_incident_neutron.from_njoy.assert_called_once_with(tape_path, temperatures=temperatures)
        mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
        assert result == target_path

    @patch("ndmanager.processors.merge_neutron_file")
    @patch("ndmanager.processors.get_available_temperature")
    @patch("ndmanager.processors.IncidentNeutron")
    @patch("ndmanager.processors.get_logger")
    def test_merge_with_existing_file(
        self, mock_get_logger, mock_incident_neutron, mock_get_available_temp, mock_merge, tmp_path
    ):
        """Test merging new temperatures with an existing file."""
        tape_path = tmp_path / "tape.file"
        tape_path.write_text("dummy content")
        target_path = tmp_path / "target.h5"
        target_path.write_text("existing hdf5 content")

        existing_temps = {300, 600}
        requested_temps = {300, 600, 900}
        mock_get_available_temp.return_value = existing_temps

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_data = Mock()
        mock_incident_neutron.from_njoy.return_value = mock_data

        result = process_neutron(target_path, tape_path, requested_temps)

        mock_get_available_temp.assert_called_once_with(target_path)
        mock_incident_neutron.from_njoy.assert_called_once_with(tape_path, temperatures={900})
        mock_data.export_to_hdf5.assert_called_once()
        mock_merge.assert_called_once()
        assert result == target_path

    @patch("ndmanager.processors.get_available_temperature")
    @patch("ndmanager.processors.get_logger")
    def test_no_new_temperatures_needed(self, mock_get_logger, mock_get_available_temp, tmp_path):
        """Test when all requested temperatures already exist."""
        tape_path = tmp_path / "tape.file"
        tape_path.write_text("dummy content")
        target_path = tmp_path / "target.h5"
        target_path.write_text("existing hdf5 content")

        temperatures = {300, 600, 900}
        mock_get_available_temp.return_value = temperatures

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        result = process_neutron(target_path, tape_path, temperatures)

        mock_logger.info.assert_any_call("No new processing is necessary, exiting")
        assert result == target_path


class TestProcessPhoton:
    """Test the process_photon function."""

    def test_nonexistent_photo_file_raises_error(self, tmp_path):
        """Test that ValueError is raised when photo file does not exist."""
        with pytest.raises(ValueError, match="Photon ENDF6 file.*does not exist"):
            process_photon(tmp_path / "target.h5", tmp_path / "missing.endf6")

    def test_nonexistent_ard_file_raises_error(self, tmp_path):
        """Test that ValueError is raised when ARD file does not exist."""
        photo_path = tmp_path / "photo.endf6"
        photo_path.write_text("dummy photo content")

        with pytest.raises(ValueError, match="Atomic relaxation data ENDF6 file.*does not exist"):
            process_photon(tmp_path / "target.h5", photo_path, tmp_path / "missing_ard.endf6")

    @patch("ndmanager.processors.IncidentPhoton")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file_without_ard(self, mock_get_logger, mock_incident_photon, tmp_path):
        """Test creating a new photon HDF5 file without ARD."""
        photo_path = tmp_path / "photo.endf6"
        photo_path.write_text("dummy photo content")
        target_path = tmp_path / "target.h5"

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_data = Mock()
        mock_incident_photon.from_endf.return_value = mock_data

        result = process_photon(target_path, photo_path)

        assert mock_logger.info.call_count >= 2
        mock_logger.info.assert_any_call("Processing photon data for %s", "target")
        mock_incident_photon.from_endf.assert_called_once_with(photo_path, None)
        mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
        assert result == target_path

    @patch("ndmanager.processors.IncidentPhoton")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file_with_ard(self, mock_get_logger, mock_incident_photon, tmp_path):
        """Test creating a new photon HDF5 file with ARD."""
        photo_path = tmp_path / "photo.endf6"
        photo_path.write_text("dummy photo content")
        ard_path = tmp_path / "ard.endf6"
        ard_path.write_text("dummy ard content")
        target_path = tmp_path / "target.h5"

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_data = Mock()
        mock_incident_photon.from_endf.return_value = mock_data

        result = process_photon(target_path, photo_path, ard_path)

        mock_incident_photon.from_endf.assert_called_once_with(photo_path, ard_path)
        mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
        assert result == target_path

    @patch("ndmanager.processors.get_logger")
    def test_existing_file_skips_processing(self, mock_get_logger, tmp_path):
        """Test that existing files are not reprocessed."""
        photo_path = tmp_path / "photo.endf6"
        photo_path.write_text("dummy photo content")
        target_path = tmp_path / "target.h5"
        target_path.write_text("existing hdf5 content")

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        result = process_photon(target_path, photo_path)

        mock_logger.info.assert_any_call(
            "Target file already exists at %s, no processing necessary", target_path
        )
        assert result == target_path


class TestProcessTsl:
    """Test the process_tsl function."""

    def test_nonexistent_neutron_file_raises_error(self, tmp_path):
        """Test that ValueError is raised when neutron file does not exist."""
        with pytest.raises(ValueError, match="Neutron ENDF6 file.*does not exist"):
            process_tsl(tmp_path / "target.h5", tmp_path / "missing.endf6", tmp_path / "tsl.endf6")

    def test_nonexistent_tsl_file_raises_error(self, tmp_path):
        """Test that ValueError is raised when TSL file does not exist."""
        neutron_path = tmp_path / "neutron.endf6"
        neutron_path.write_text("dummy neutron content")

        with pytest.raises(ValueError, match="TSL ENDF6 file.*does not exist"):
            process_tsl(tmp_path / "target.h5", neutron_path, tmp_path / "missing_tsl.endf6")

    @patch("ndmanager.processors.ThermalScattering")
    @patch("ndmanager.processors.get_logger")
    def test_create_new_file(self, mock_get_logger, mock_thermal_scattering, tmp_path):
        """Test creating a new TSL HDF5 file."""
        neutron_path = tmp_path / "neutron.endf6"
        neutron_path.write_text("dummy neutron content")
        tsl_path = tmp_path / "tsl.endf6"
        tsl_path.write_text("dummy tsl content")
        target_path = tmp_path / "target.h5"

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_data = Mock()
        mock_thermal_scattering.from_njoy.return_value = mock_data

        result = process_tsl(target_path, neutron_path, tsl_path)

        assert mock_logger.info.call_count >= 2
        mock_logger.info.assert_any_call("Processing TSL data for %s", "target")
        mock_thermal_scattering.from_njoy.assert_called_once_with(neutron_path, tsl_path)
        mock_data.export_to_hdf5.assert_called_once_with(target_path, "w")
        assert result == target_path

    @patch("ndmanager.processors.get_logger")
    def test_existing_file_skips_processing(self, mock_get_logger, tmp_path):
        """Test that existing files are not reprocessed."""
        neutron_path = tmp_path / "neutron.endf6"
        neutron_path.write_text("dummy neutron content")
        tsl_path = tmp_path / "tsl.endf6"
        tsl_path.write_text("dummy tsl content")
        target_path = tmp_path / "target.h5"
        target_path.write_text("existing hdf5 content")

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        result = process_tsl(target_path, neutron_path, tsl_path)

        mock_logger.info.assert_any_call(
            "Target file already exists at %s, no processing necessary", target_path
        )
        assert result == target_path


class TestLogPathCreation:
    """Test that log paths are derived correctly from the target path."""

    @pytest.mark.parametrize("processor,mock_target,make_inputs", [
        (
            process_neutron,
            "ndmanager.processors.IncidentNeutron",
            lambda d: [d / "subdir" / "target.h5", d / "tape.file", {300}],
        ),
        (
            process_photon,
            "ndmanager.processors.IncidentPhoton",
            lambda d: [d / "subdir" / "target.h5", d / "photo.endf6"],
        ),
        (
            process_tsl,
            "ndmanager.processors.ThermalScattering",
            lambda d: [d / "subdir" / "target.h5", d / "neutron.endf6", d / "tsl.endf6"],
        ),
    ])
    @patch("ndmanager.processors.get_logger")
    def test_log_path(self, mock_get_logger, tmp_path, processor, mock_target, make_inputs):
        """Test that each processor derives the log path from target.parent/logs/target.stem.log."""
        inputs = make_inputs(tmp_path)
        for p in inputs[1:]:
            if isinstance(p, Path):
                p.write_text("content")

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch(mock_target) as mock_cls:
            mock_cls.from_njoy.return_value = Mock()
            mock_cls.from_endf.return_value = Mock()
            processor(*inputs)

        expected_log_path = tmp_path / "subdir" / "logs" / "target.log"
        mock_get_logger.assert_called_once_with(expected_log_path)
