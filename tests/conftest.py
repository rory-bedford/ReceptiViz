"""Test configuration and shared fixtures for pytest."""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from receptual.processing.data_manager import EncoderDataManager


# Create processor fixture
@pytest.fixture
def processor():
	"""Create a fresh DataManager for each test."""
	return EncoderDataManager()


# Fixture for creating temporary test files
@pytest.fixture
def create_temp_file():
	"""Create a temporary file that is automatically cleaned up."""
	temp_files = []

	def _create_temp():
		tmp = tempfile.NamedTemporaryFile(suffix='.npy', delete=False)
		path = Path(tmp.name)
		tmp.close()
		temp_files.append(path)
		return path

	yield _create_temp

	# Clean up all created temp files after the test
	for path in temp_files:
		if path.exists():
			path.unlink()


# Data generator fixtures
@pytest.fixture
def valid_activity_1d(create_temp_file):
	"""Generate a valid 1D activity array."""
	np.random.seed(42)
	data = np.random.normal(0, 1, (100, 1))
	path = create_temp_file()
	np.save(path, data)
	return path, data
