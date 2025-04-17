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
	data = np.random.normal(0, 1, 100)
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def valid_activity_1d_long(create_temp_file):
	"""Generate a longer valid 1D activity array."""
	np.random.seed(43)
	data = np.random.normal(0, 1, 1000)
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def valid_stimulus_1d(create_temp_file):
	"""Generate a valid 1D stimulus array."""
	np.random.seed(44)
	data = np.random.normal(0, 1, 100)
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def valid_stimulus_2d(create_temp_file):
	"""Generate a valid 2D stimulus array."""
	np.random.seed(45)
	data = np.random.normal(0, 1, (100, 100))
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def valid_stimulus_3d(create_temp_file):
	"""Generate a valid 3D stimulus array."""
	np.random.seed(46)
	data = np.random.normal(0, 1, (100, 10, 10))
	path = create_temp_file()
	np.save(path, data)
	return path, data


# Invalid data fixtures
@pytest.fixture
def invalid_activity_2d(create_temp_file):
	"""Generate an invalid 2D activity array (should be 1D)."""
	np.random.seed(47)
	data = np.random.normal(0, 1, (100, 10))
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def invalid_activity_short(create_temp_file):
	"""Generate an activity array that's too short."""
	np.random.seed(48)
	data = np.random.normal(0, 1, 5)
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def invalid_activity_nans(create_temp_file):
	"""Generate an activity array with NaNs."""
	np.random.seed(49)
	data = np.random.normal(0, 1, 100)
	data[10:20] = np.nan
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def invalid_stimulus_short(create_temp_file):
	"""Generate a stimulus array that's too short."""
	np.random.seed(50)
	data = np.random.normal(0, 1, (5, 10, 10))
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def invalid_stimulus_nans(create_temp_file):
	"""Generate a stimulus array with NaNs."""
	np.random.seed(51)
	data = np.random.normal(0, 1, (100, 10, 10))
	data[10:20, :, :] = np.nan
	path = create_temp_file()
	np.save(path, data)
	return path, data


@pytest.fixture
def invalid_stimulus_wrong_type(create_temp_file):
	"""Generate a stimulus array with wrong data type."""
	data = np.ones((100, 10, 10), dtype=np.complex128)
	path = create_temp_file()
	np.save(path, data)
	return path, data


# Incompatible data fixtures
@pytest.fixture
def incompatible_arrays(create_temp_file):
	"""Generate incompatible activity and stimulus arrays."""
	np.random.seed(52)

	# Create arrays with different time dimensions
	activity_path = create_temp_file()
	stimulus_path = create_temp_file()

	activity_data = np.random.normal(0, 1, 50)
	stimulus_data = np.random.normal(0, 1, (100, 10, 10))

	np.save(activity_path, activity_data)
	np.save(stimulus_path, stimulus_data)

	yield activity_path, activity_data, stimulus_path, stimulus_data
