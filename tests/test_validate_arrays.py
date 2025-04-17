"""Tests for the receptive field validation functionality."""

import numpy as np


class TestEncoderDataManagerValidation:
	def test_validate_valid_activity_file(self, processor, valid_activity_1d):
		file_path, expected_data = valid_activity_1d

		is_valid, errors, data = processor.validate_file(str(file_path), 'activity')

		assert is_valid is True
		assert not errors
		assert data is not None
		assert data.shape == (100,)
		assert np.array_equal(data, expected_data)

	def test_validate_invalid_activity_2d(self, processor, invalid_activity_2d):
		file_path, _ = invalid_activity_2d

		is_valid, errors, data = processor.validate_file(str(file_path), 'activity')

		assert is_valid is False
		assert any('must be 1D' in error for error in errors)
		assert data is None

	def test_validate_short_activity(self, processor, invalid_activity_short):
		file_path, _ = invalid_activity_short

		is_valid, errors, data = processor.validate_file(str(file_path), 'activity')

		assert is_valid is False
		assert any('too small' in error for error in errors)
		assert data is None

	def test_validate_valid_stimulus(self, processor, valid_stimulus_2d):
		file_path, expected_data = valid_stimulus_2d

		is_valid, errors, data = processor.validate_file(str(file_path), 'stimulus')

		assert is_valid is True
		assert not errors
		assert data is not None
		assert data.shape == (100, 100)
		assert np.array_equal(data, expected_data)

	def test_validate_valid_1d_stimulus(self, processor, valid_stimulus_1d):
		file_path, expected_data = valid_stimulus_1d

		is_valid, errors, data = processor.validate_file(str(file_path), 'stimulus')

		assert is_valid is True
		assert not errors
		assert data is not None
		assert data.shape == (100,)
		assert np.array_equal(data, expected_data)

	def test_validate_incompatible_arrays(self, processor, incompatible_arrays):
		activity_path, activity_data, stimulus_path, _ = incompatible_arrays

		# Load activity with 50 timepoints
		activity_valid, _, activity_data = processor.validate_file(
			str(activity_path), 'activity'
		)
		assert activity_valid is True
		processor.set_activity(activity_data)

		# Load stimulus with 100 timepoints
		stimulus_valid, errors, _ = processor.validate_file(
			str(stimulus_path), 'stimulus'
		)

		# Should fail due to incompatible time dimensions
		assert stimulus_valid is False
		assert any('must match activity length' in error for error in errors)

	def test_validate_incompatible_arrays_reversed(
		self, processor, incompatible_arrays
	):
		activity_path, _, stimulus_path, stimulus_data = incompatible_arrays

		# First load stimulus with 100 timepoints
		stimulus_valid, _, stimulus_data = processor.validate_file(
			str(stimulus_path), 'stimulus'
		)
		assert stimulus_valid is True
		processor.set_stimulus(stimulus_data)

		# Then try to load activity with 50 timepoints (should fail)
		activity_valid, errors, _ = processor.validate_file(
			str(activity_path), 'activity'
		)

		# Should fail due to incompatible time dimensions
		assert activity_valid is False
		assert any('must match stimulus length' in error for error in errors)
