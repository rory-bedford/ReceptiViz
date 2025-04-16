"""Tests for the encoder functionality."""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from receptual import encoder, receptive_field
from .naive_implementations import naive_encoder


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

	def test_large_arrays_against_naive(self):
		"""
		Test encoding with large arrays against naive implementation.
		Array sizes:
		- stimulus: (200, 10, 20) 	           # 200 time points, spatial dimension length 10, 20
		- receptive_field: (20, 30, 10, 20)    # 20-element kernel for 30 neurons across spatial dims
		- expected_output: (200, 30)           # output activity for 30 neurons across 2000 time points
		Number tests: 10
		"""

		np.random.seed(42)  # For reproducibility

		for i in range(10):
			# Generate random test inputs with different but reproducible seeds
			np.random.seed(42 + i)
			stimulus = np.random.rand(200, 10, 20)
			receptive_field = np.random.rand(10, 30, 10, 20)

			# Expected output (calculated using naive implementation)
			expected_output = naive_encoder(stimulus, receptive_field)

			# Call the encoder function
			result = encoder(stimulus, receptive_field)

			# Assert the result matches expected output
			assert result.shape == expected_output.shape
			np.testing.assert_allclose(result, expected_output, rtol=1e-5)


def generate_temporally_colored_noise(shape, rho=0.5, seed=None):
	if seed is not None:
		np.random.seed(seed)
	T, W = shape
	noise = np.zeros((T, W))
	noise[0] = np.random.randn(W)  # initial frame
	for t in range(1, T):
		noise[t] = rho * noise[t - 1] + np.sqrt(1 - rho**2) * np.random.randn(W)
	return noise


def generate_spatially_colored_noise(shape, sigma=0.5, seed=None):
	if seed is not None:
		np.random.seed(seed)
	T, W = shape
	noise = np.random.randn(T, W)  # white noise
	for t in range(T):
		noise[t] = gaussian_filter1d(noise[t], sigma=sigma, mode='reflect')
	return noise


def generate_spatiotemporally_colored_noise(shape, rho=0.5, sigma=0.5, seed=None):
	if seed is not None:
		np.random.seed(seed)
	T, W = shape
	noise = np.zeros((T, W))
	noise[0] = gaussian_filter1d(np.random.randn(W), sigma=sigma, mode='reflect')
	for t in range(1, T):
		white = np.random.randn(W)
		white_smoothed = gaussian_filter1d(white, sigma=sigma, mode='reflect')
		noise[t] = rho * noise[t - 1] + np.sqrt(1 - rho**2) * white_smoothed
	return noise


class TestReceptiveField:
	def test_rf_1D(self):
		"""
		Test 1D receptive field solver with a single neuron.

		Array sizes:
		- stimulus: (6,)             # 1D time series
		- activity: (6, 1)           # activity for 1 neuron
		- kernel_size: 3             # 3-element kernel
		- expected_output: (3, 1)    # Receptive field for 1 neuron
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
		- activity: (6, 2)           # activity for 2 neurons
		- kernel_size: 3             # 3-element kernel
		- expected_output: (3, 2)    # Receptive field for 2 neurons
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

	def test_rf_multiple_dimensions_no_time(self):
		"""
		Test multidimensional stimulus receptive field solver.

		Array sizes:
		- stimulus: (1, 2)           # 1 time points, spatial dimension length 2
		- activity: (1, 1)           # activity for 1 neuron
		- kernel_size: 1             # 1-element kernel
		- expected_output: (1, 1, 2) # Receptive field for 1 neuron across spatial dimensions
		"""
		# Define test inputs
		stimulus = np.array([[1, 2], [3, 4], [5, 6]])
		activity = np.array([[22], [58], [94]])

		# Expected output (calculated manually)
		expected_rf = np.array([14, 4])[None, None, :]

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=1)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_multiple_dimensions(self):
		"""
		Test multidimensional stimulus receptive field solver.

		Array sizes:
		- stimulus: (6, 2)           # 6 time points, spatial dimension length 2
		- activity: (6, 1)           # activity for 1 neuron
		- kernel_size: 3             # 3-element kernel
		- expected_output: (3, 1, 2) # Receptive field for 1 neuron across spatial dimensions
		"""
		# Define test inputs
		np.random.seed(123)
		stimulus = np.random.randn(6, 2)
		expected_rf = np.random.randn(3, 1, 2)
		activity = encoder(stimulus, expected_rf)

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_multi_neurons_and_space(self):
		"""
		Test receptive field solver with multiple neurons and spatial dimensions.
		Array sizes:
		- stimulus: (6, 2)              # 6 time points, spatial dimension length 2
		- activity: (6, 2)              # activity for 2 neurons
		- kernel_size: 3                # 3-element kernel
		- expected_output: (3, 2, 2)    # receptive field for 2 neurons across spatial dimensions
		"""
		# Define test inputs
		np.random.seed(124)
		stimulus = np.random.randn(6, 2)
		expected_rf = np.random.randn(3, 2, 2)
		activity = encoder(stimulus, expected_rf)

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=3)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_coloured_time(self):
		"""
		Test receptive field solver with temporally colored noise.
		Array sizes:
		- stimulus: (200, 10) 	         # 200 time points, spatial dimension length 10
		- activity: (200, 30)            # activity for 30 neurons
		- kernel_size: 20                # 20-element kernel
		- expected_output: (20, 30, 10)  # receptive field for 30 neurons across spatial dimensions
		"""
		# Generate temporally colored noise
		np.random.seed(125)
		stimulus = generate_temporally_colored_noise((200, 10), seed=125)

		# Define receptive field and activity
		expected_rf = np.random.randn(20, 30, 10)
		activity = encoder(stimulus, expected_rf)

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=20)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_coloured_space(self):
		"""
		Test receptive field solver with temporally colored noise.
		Array sizes:
		- stimulus: (200, 10) 	         # 200 time points, spatial dimension length 10
		- activity: (200, 30)            # activity for 30 neurons
		- kernel_size: 20                # 20-element kernel
		- expected_output: (20, 30, 10)  # receptive field for 30 neurons across spatial dimensions
		"""
		# Generate temporally colored noise
		np.random.seed(126)
		stimulus = generate_spatially_colored_noise((200, 10), seed=126)

		# Define receptive field and activity
		expected_rf = np.random.randn(20, 30, 10)
		activity = encoder(stimulus, expected_rf)

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=20)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_coloured_space_and_time(self):
		"""
		Test receptive field solver with temporally colored noise.
		Array sizes:
		- stimulus: (200, 10) 	         # 200 time points, spatial dimension length 10
		- activity: (200, 30)            # activity for 30 neurons
		- kernel_size: 20                # 20-element kernel
		- expected_output: (20, 30, 10)  # receptive field for 30 neurons across spatial dimensions
		"""
		# Generate temporally colored noise
		np.random.seed(127)
		stimulus = generate_spatiotemporally_colored_noise((200, 10), seed=127)

		# Define receptive field and activity
		expected_rf = np.random.randn(20, 30, 10)
		activity = encoder(stimulus, expected_rf)

		# Call the rf function
		result = receptive_field(stimulus, activity, kernel_size=20)

		# Assert the result matches expected output
		assert result.shape == expected_rf.shape
		np.testing.assert_allclose(result, expected_rf, rtol=1e-5)

	def test_rf_large_arrays(self):
		"""
		Test receptive field solver with large arrays against naive implementation.
		Array sizes:
		- stimulus: (200, 10, 5) 	           # 200 time points, spatial dimension length 10, 5
		- receptive_field: (20, 30, 10, 5)     # 20-element kernel for 30 neurons across spatial dims
		- expected_output: (200, 30)           # output activity for 30 neurons across 2000 time points
		Number tests: 2
		"""

		for i in range(2):
			# Generate random test inputs with different but reproducible seeds
			np.random.seed(142 + i)
			stimulus = np.random.rand(200, 10, 5)
			input_rf = np.random.rand(20, 30, 10, 5)

			# Expected output (calculated using naive implementation)
			activity = naive_encoder(stimulus, input_rf)

			# Call the encoder function
			computed_rf = receptive_field(stimulus, activity, kernel_size=20)

			# Assert the result matches expected output
			assert computed_rf.shape == input_rf.shape
			np.testing.assert_allclose(computed_rf, input_rf, rtol=1e-5)
