"""Tests for the encoder functionality."""

import numpy as np
from receptual import encoder


class TestEncoder:
	def test_encoder_1D(self):
		"""
		Test 1D stimulus encoding with a single neuron.

		Array sizes:
		- stimulus: (6,)             # 1D time series
		- receptive_field: (3, 1)    # 3-element kernel for 1 neuron
		- expected_output: (6, 1)    # Output activity for 1 neuron across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
		receptive_field = np.array([0.5, 0.25, 0.25])[:, np.newaxis]

		# Expected output (calculated manually)
		expected_output = np.array([0.25, 0.75, 1.75, 2.75, 3.75, 4.75])[:, np.newaxis]

		# Call the encoder function
		result = encoder(stimulus, receptive_field)

		# Assert the result matches expected output
		assert result.shape == expected_output.shape
		np.testing.assert_allclose(result, expected_output, rtol=1e-5)

	def test_encoder_multiple_neurons(self):
		"""
		Test 1D stimulus encoding with multiple neurons.

		Array sizes:
		- stimulus: (6,)             # 1D time series
		- receptive_field: (3, 2)    # 3-element kernel for 2 neurons
		- expected_output: (6, 2)    # Output activity for 2 neurons across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
		receptive_field = np.array([[0.5, 0.25, 0.25], [1.0, 1.5, 2.0]]).T

		# Expected output (calculated manually)
		expected_output = np.array([
			[0.25, 0.75, 1.75, 2.75, 3.75, 4.75],
			[2.0, 5.5, 10.0, 14.5, 19.0, 23.5],
		]).T

		# Call the encoder function
		result = encoder(stimulus, receptive_field)

		# Assert the result matches expected output
		assert result.shape == expected_output.shape
		np.testing.assert_allclose(result, expected_output, rtol=1e-5)

	def test_encoder_multiple_dimensions(self):
		"""
		Test multidimensional stimulus encoding.

		Array sizes:
		- stimulus: (6, 2)           # 6 time points, spatial dimension length 2
		- receptive_field: (3, 1, 2) # 3-element kernel for 1 neuron across spatial dim
		- expected_output: (6, 1)    # Output activity for 1 neuron across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([
			[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
			[7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
		]).T
		receptive_field = np.array([[0.5, 0.25, 0.25], [1.0, 1.5, 2.0]]).T[
			:, np.newaxis, :
		]

		# Expected output (calculated manually)
		expected_output = np.array([14.25, 27.25, 38.75, 44.25, 49.75, 55.25])[
			:, np.newaxis
		]

		# Call the encoder function
		result = encoder(stimulus, receptive_field)

		# Assert the result matches expected output
		assert result.shape == expected_output.shape
		np.testing.assert_allclose(result, expected_output, rtol=1e-5)

	def test_encoder_multi_neurons_and_space(self):
		"""
		Test encoding with multiple neurons and spatial dimensions.
		Array sizes:
		- stimulus: (6, 2, 3)           # 6 time points, 2 spatial dimensions
		- receptive_field: (3, 2, 2, 3) # 3-element kernel for 2 neurons across spatial dims
		- expected_output: (6, 2)       # output activity for 2 neurons across 6 time points
		"""
		# define test inputs
		stimulus = np.array([
			[[3.0, 7.0, 10.0], [5.0, 4.0, 4.0]],
			[[5.0, 5.0, 1.0], [6.0, 1.0, 3.0]],
			[[1.0, 3.0, 9.0], [4.0, 3.0, 3.0]],
			[[10.0, 2.0, 9.0], [3.0, 6.0, 3.0]],
			[[10.0, 6.0, 9.0], [5.0, 6.0, 10.0]],
			[[8.0, 3.0, 7.0], [8.0, 2.0, 9.0]],
		])

		receptive_field = np.array([
			[[[4.0, 5.0, 4.0], [2.0, 1.0, 1.0]], [[7.0, 3.0, 5.0], [6.0, 4.0, 1.0]]],
			[[[8.0, 8.0, 5.0], [9.0, 5.0, 5.0]], [[3.0, 6.0, 7.0], [4.0, 9.0, 10.0]]],
			[[[2.0, 4.0, 6.0], [6.0, 10.0, 8.0]], [[1.0, 2.0, 2.0], [3.0, 9.0, 9.0]]],
		])

		# Expected output (calculated manually)
		expected_output = np.array([
			[196.0, 124.0],
			[321.0, 288.0],
			[410.0, 348.0],
			[392.0, 377.0],
			[550.0, 500.0],
			[609.0, 620.0],
		])

		# Call the encoder function
		result = encoder(stimulus, receptive_field)

		# Assert the result matches expected output
		assert result.shape == expected_output.shape
		np.testing.assert_allclose(result, expected_output, rtol=1e-5)
