"""Tests for the utils module."""

import logging
import tempfile
import warnings
from pathlib import Path

import pytest

from ndmanager.utils import get_hdf5, get_logger


class TestGetHdf5:
    """Test the get_hdf5 function."""

    def test_nonexistent_library_raises_error(self):
        """Test that ValueError is raised when library doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = Path(tmpdir)
                
                with pytest.raises(ValueError, match="Library 'nonexistent' does not exist"):
                    get_hdf5("nonexistent", "neutron", "U235")
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path

    def test_successful_retrieval_with_directory_node(self):
        """Test successful retrieval when XML has directory node."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create library structure
            lib_dir = tmpdir_path / "testlib"
            lib_dir.mkdir()
            data_dir = lib_dir / "data"
            data_dir.mkdir()
            
            # Create cross_sections.xml with directory node
            xml_content = """<?xml version="1.0"?>
<cross_sections>
  <directory>data</directory>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="Pu239" path="Pu239.h5" type="neutron"/>
</cross_sections>
"""
            (lib_dir / "cross_sections.xml").write_text(xml_content)
            
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = tmpdir_path
                
                result = get_hdf5("testlib", "neutron", "U235")
                
                # The function returns Path(directory) / path, which is relative
                assert result == Path("data") / "U235.h5"
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path

    def test_successful_retrieval_without_directory_node(self):
        """Test successful retrieval when XML has no directory node."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create library structure
            lib_dir = tmpdir_path / "testlib"
            lib_dir.mkdir()
            
            # Create cross_sections.xml without directory node
            xml_content = """<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="H1" path="H1.h5" type="neutron"/>
</cross_sections>
"""
            (lib_dir / "cross_sections.xml").write_text(xml_content)
            
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = tmpdir_path
                
                result = get_hdf5("testlib", "neutron", "U235")
                
                # Should use parent directory when no directory node
                assert result == lib_dir / "U235.h5"
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path

    def test_nuclide_not_found_raises_error(self):
        """Test that ValueError is raised when nuclide not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create library structure
            lib_dir = tmpdir_path / "testlib"
            lib_dir.mkdir()
            
            # Create cross_sections.xml
            xml_content = """<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="Pu239" path="Pu239.h5" type="neutron"/>
</cross_sections>
"""
            (lib_dir / "cross_sections.xml").write_text(xml_content)
            
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = tmpdir_path
                
                with pytest.raises(ValueError, match="Can't find neutron xs for U238"):
                    get_hdf5("testlib", "neutron", "U238")
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path

    def test_sublibrary_type_not_found_raises_error(self):
        """Test that ValueError is raised when sublibrary type doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create library structure
            lib_dir = tmpdir_path / "testlib"
            lib_dir.mkdir()
            
            # Create cross_sections.xml with only neutron data
            xml_content = """<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
</cross_sections>
"""
            (lib_dir / "cross_sections.xml").write_text(xml_content)
            
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = tmpdir_path
                
                # Try to get photon data when only neutron exists
                with pytest.raises(ValueError, match="Can't find photon xs for U235"):
                    get_hdf5("testlib", "photon", "U235")
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path

    def test_multiple_libraries_returns_correct_one(self):
        """Test that correct library is returned when multiple exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create library structure
            lib_dir = tmpdir_path / "testlib"
            lib_dir.mkdir()
            
            # Create cross_sections.xml with multiple libraries
            xml_content = """<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235_neutron.h5" type="neutron"/>
  <library materials="U235" path="U235_photon.h5" type="photon"/>
  <library materials="Pu239" path="Pu239_neutron.h5" type="neutron"/>
</cross_sections>
"""
            (lib_dir / "cross_sections.xml").write_text(xml_content)
            
            import ndmanager.utils
            original_path = ndmanager.utils.NDMANAGER_HDF5
            try:
                ndmanager.utils.NDMANAGER_HDF5 = tmpdir_path
                
                # Get neutron data
                result_neutron = get_hdf5("testlib", "neutron", "U235")
                assert result_neutron == lib_dir / "U235_neutron.h5"
                
                # Get photon data
                result_photon = get_hdf5("testlib", "photon", "U235")
                assert result_photon == lib_dir / "U235_photon.h5"
                
                # Get different nuclide
                result_pu = get_hdf5("testlib", "neutron", "Pu239")
                assert result_pu == lib_dir / "Pu239_neutron.h5"
            finally:
                ndmanager.utils.NDMANAGER_HDF5 = original_path


class TestGetLogger:
    """Test the get_logger function."""

    def test_creates_logger_with_correct_name(self):
        """Test that logger is created with name derived from file stem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            
            assert logger.name == "test"
            assert isinstance(logger, logging.Logger)

    def test_creates_parent_directories(self):
        """Test that parent directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "logs" / "subdir" / "test.log"
            
            assert not log_path.parent.exists()
            
            logger = get_logger(log_path)
            
            assert log_path.parent.exists()

    def test_logger_writes_to_file(self):
        """Test that logger writes messages to the log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            logger.info("Test message")
            
            # Flush handlers to ensure write
            for handler in logger.handlers:
                handler.flush()
            
            assert log_path.exists()
            content = log_path.read_text()
            assert "Test message" in content
            assert "[INFO" in content

    def test_logger_level_is_info(self):
        """Test that logger level is set to INFO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            
            assert logger.level == logging.INFO

    def test_formatter_includes_timestamp(self):
        """Test that log messages include timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            logger.info("Test message")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            content = log_path.read_text()
            # Check for timestamp pattern YYYY-MM-DD HH:MM:SS
            import re
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, content)

    def test_warnings_redirected_to_logger(self):
        """Test that Python warnings are redirected to the logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            
            # Issue a warning
            warnings.warn("This is a test warning")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            content = log_path.read_text()
            assert "This is a test warning" in content
            assert "[WARNING" in content

    def test_file_handler_attached(self):
        """Test that a FileHandler is attached to the logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger = get_logger(log_path)
            
            # Check that at least one handler is a FileHandler
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) > 0

    def test_multiple_calls_same_path(self):
        """Test behavior when get_logger is called multiple times with same path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path = tmpdir_path / "test.log"
            
            logger1 = get_logger(log_path)
            logger2 = get_logger(log_path)
            
            # Both should return the same logger instance (same name)
            assert logger1.name == logger2.name

    def test_different_loggers_different_names(self):
        """Test that different log files create loggers with different names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_path1 = tmpdir_path / "test1.log"
            log_path2 = tmpdir_path / "test2.log"
            
            logger1 = get_logger(log_path1)
            logger2 = get_logger(log_path2)
            
            assert logger1.name == "test1"
            assert logger2.name == "test2"
            assert logger1.name != logger2.name

    def test_existing_directory_works(self):
        """Test that logger works when parent directory already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            log_dir = tmpdir_path / "logs"
            log_dir.mkdir()
            log_path = log_dir / "test.log"
            
            logger = get_logger(log_path)
            logger.info("Test message")
            
            for handler in logger.handlers:
                handler.flush()
            
            assert log_path.exists()
            content = log_path.read_text()
            assert "Test message" in content
