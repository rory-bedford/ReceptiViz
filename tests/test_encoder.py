"""Tests for the encoder functionality."""

import numpy as np
from receptual import encoder, receptive_field
import pytest


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

	def test_encoder_all_dims_different(self):
		"""
		Test encoding with multiple neurons and spatial dimensions of
		different sizes.
		Array sizes:
		- stimulus: (6, 2, 3)           # 6 time points, spatial dimensions (2, 3)
		- receptive_field: (4, 5, 2, 3) # 4-element kernel for 5 neurons across spatial dims
		- expected_output: (6, 5)       # output activity for 2 neurons across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([
			[[8, 3, 5], [1, 6, 9]],
			[[6, 10, 1], [10, 10, 6]],
			[[4, 9, 5], [9, 1, 8]],
			[[5, 5, 6], [4, 8, 10]],
			[[9, 1, 8], [4, 6, 4]],
			[[8, 9, 3], [9, 5, 3]],
		])
		receptive_field = np.array([
			[
				[[8, 1, 8], [4, 1, 1]],
				[[8, 2, 6], [7, 10, 9]],
				[[10, 7, 1], [2, 9, 8]],
				[[4, 9, 9], [7, 10, 2]],
				[[8, 10, 1], [8, 1, 5]],
			],
			[
				[[8, 8, 7], [7, 6, 9]],
				[[10, 7, 9], [5, 10, 6]],
				[[10, 1, 9], [5, 6, 3]],
				[[10, 3, 2], [6, 9, 4]],
				[[5, 3, 6], [8, 4, 5]],
			],
			[
				[[7, 2, 4], [7, 4, 6]],
				[[10, 8, 1], [10, 4, 9]],
				[[8, 3, 3], [9, 8, 3]],
				[[3, 2, 7], [10, 10, 9]],
				[[8, 1, 4], [7, 2, 1]],
			],
			[
				[[9, 9, 9], [5, 10, 3]],
				[[4, 2, 9], [1, 7, 7]],
				[[5, 2, 5], [9, 1, 7]],
				[[10, 6, 10], [6, 6, 1]],
				[[4, 9, 3], [4, 8, 3]],
			],
		])

		expected_output = np.array([
			[236.0, 189.0, 149.0, 199.0, 153.0],
			[488.0, 399.0, 369.0, 472.0, 370.0],
			[700.0, 751.0, 666.0, 706.0, 494.0],
			[900.0, 1070.0, 807.0, 914.0, 701.0],
			[845.0, 991.0, 818.0, 994.0, 730.0],
			[871.0, 872.0, 781.0, 916.0, 786.0],
		])

		# Call the encoder function
		result = encoder(stimulus, receptive_field)

		# Assert the result matches expected output
		assert result.shape == expected_output.shape
		np.testing.assert_allclose(result, expected_output, rtol=1e-5)


@pytest.mark.skip(reason='Temporarily disabled for debugging')
class TestReceptiveField:
	def test_rf_1D(self):
		"""
		Test 1D receptive field solver with a single neuron.

		Array sizes:
		- stimulus: (6,)             # 1D time series
		- receptive_field: (3, 1)    # 3-element kernel for 1 neuron
		- expected_output: (6, 1)    # Output activity for 1 neuron across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
		activity = np.array([0.25, 0.75, 1.75, 2.75, 3.75, 4.75])[:, np.newaxis]

		# Expected output (calculated manually)
		expected_rf = np.array([0.5, 0.25, 0.25])[:, np.newaxis]

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_multiple_neurons(self):
		"""
		Test 1D receptive field solver with multiple neurons.

		Array sizes:
		- stimulus: (6,)             # 1D time series
		- receptive_field: (3, 2)    # 3-element kernel for 2 neurons
		- expected_output: (6, 2)    # Output activity for 2 neurons across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
		activity = np.array([
			[0.25, 0.75, 1.75, 2.75, 3.75, 4.75],
			[2.0, 5.5, 10.0, 14.5, 19.0, 23.5],
		]).T

		# Expected output (calculated manually)
		expected_rf = np.array([[0.5, 0.25, 0.25], [1.0, 1.5, 2.0]]).T

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_multiple_dimensions(self):
		"""
		Test multidimensional stimulus receptive field solver.

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

		activity = np.array([14.25, 27.25, 38.75, 44.25, 49.75, 55.25])[:, np.newaxis]

		# Expected output (calculated manually)
		expected_rf = np.array([[0.5, 0.25, 0.25], [1.0, 1.5, 2.0]]).T[:, np.newaxis, :]

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_multi_neurons_and_space(self):
		"""
		Test receptive field solver with multiple neurons and spatial dimensions.
		Array sizes:
		- stimulus: (6, 2, 3)           # 6 time points, 2 spatial dimensions
		- receptive_field: (3, 2, 2, 3) # 3-element kernel for 2 neurons across spatial dims
		- expected_output: (6, 2)       # output activity for 2 neurons across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([
			[[3.0, 7.0, 10.0], [5.0, 4.0, 4.0]],
			[[5.0, 5.0, 1.0], [6.0, 1.0, 3.0]],
			[[1.0, 3.0, 9.0], [4.0, 3.0, 3.0]],
			[[10.0, 2.0, 9.0], [3.0, 6.0, 3.0]],
			[[10.0, 6.0, 9.0], [5.0, 6.0, 10.0]],
			[[8.0, 3.0, 7.0], [8.0, 2.0, 9.0]],
		])

		activity = np.array([
			[196.0, 124.0],
			[321.0, 288.0],
			[410.0, 348.0],
			[392.0, 377.0],
			[550.0, 500.0],
			[609.0, 620.0],
		])

		# Expected output (calculated manually)
		expected_rf = np.array([
			[[[4.0, 5.0, 4.0], [2.0, 1.0, 1.0]], [[7.0, 3.0, 5.0], [6.0, 4.0, 1.0]]],
			[[[8.0, 8.0, 5.0], [9.0, 5.0, 5.0]], [[3.0, 6.0, 7.0], [4.0, 9.0, 10.0]]],
			[[[2.0, 4.0, 6.0], [6.0, 10.0, 8.0]], [[1.0, 2.0, 2.0], [3.0, 9.0, 9.0]]],
		])

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_all_dims_different(self):
		"""
		Test receptive field solver with multiple neurons and spatial dimensions of
		different sizes.
		Array sizes:
		- stimulus: (6, 2, 3)           # 6 time points, spatial dimensions (2, 3)
		- receptive_field: (4, 5, 2, 3) # 4-element kernel for 5 neurons across spatial dims
		- expected_output: (6, 5)       # output activity for 5 neurons across 6 time points
		"""
		# Define test inputs
		stimulus = np.array([
			[[3.0, 7.0, 10.0], [5.0, 4.0, 4.0]],
			[[5.0, 5.0, 1.0], [6.0, 1.0, 3.0]],
			[[1.0, 3.0, 9.0], [4.0, 3.0, 3.0]],
			[[10.0, 2.0, 9.0], [3.0, 6.0, 3.0]],
			[[10.0, 6.0, 9.0], [5.0, 6.0, 10.0]],
			[[8.0, 3.0, 7.0], [8.0, 2.0, 9.0]],
		])

		activity = np.array([
			[196.0, 124.0, 204.0, 150.0, 300.0],
			[321.0, 288.0, 350.0, 300.0, 400.0],
			[410.0, 348.0, 500.0, 400.0, 600.0],
			[392.0, 377.0, 450.0, 350.0, 550.0],
			[550.0, 500.0, 600.0, 500.0, 700.0],
			[609.0, 620.0, 700.0, 600.0, 800.0],
		])

		# Expected output (calculated manually)
		expected_rf = np.array([
			[[[4.0, 5.0, 4.0], [2.0, 1.0, 1.0]], [[7.0, 3.0, 5.0], [6.0, 4.0, 1.0]]],
			[[[8.0, 8.0, 5.0], [9.0, 5.0, 5.0]], [[3.0, 6.0, 7.0], [4.0, 9.0, 10.0]]],
			[[[2.0, 4.0, 6.0], [6.0, 10.0, 8.0]], [[1.0, 2.0, 2.0], [3.0, 9.0, 9.0]]],
		])

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)
		print(result)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)
