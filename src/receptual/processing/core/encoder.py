"""
Neural stimulus encoder module.

This module provides functions to encode stimuli using neural receptive fields,
implementing temporal convolution to simulate neural processing of sensory inputs.
Additionally we provide a function to compute the optimal receptive field for a given
stimulus and activity data.

Author: Rory Bedford
Date: 2025-04-14

TODO:
- Implement more efficient convolution using scipy.signal and FFT
"""

import numpy as np


def encoder(stimulus, receptive_field):
	"""Encodes a stimulus using a receptive field.

	This function performs temporal convolution of the stimulus with the
	receptive field kernel along the first dimension (axis 0).

	Args:
		stimulus: numpy.ndarray
			Input stimulus with shape:
			- axis 0: time/samples (T)
			- axis [1:]: spatial dimensions (optional)
		receptive_field: numpy.ndarray
			Receptive field kernel with shape:
			- axis 0: kernel timepoints (K) where K < T
			- axis 1: number of neurons (N)
			- axis [2:]: spatial dimensions (must match stimulus)

	Returns:
		numpy.ndarray:
			The encoded stimulus with shape:
			- axis 0: time/samples (T) (same as input)
			- axis 1: number of neurons (N)
			- axis [2:]: spatial dimensions (same as input)
	"""

	assert stimulus.ndim + 1 == receptive_field.ndim, (
		'Dimensions of arrays are not compatible'
	)
	if stimulus.ndim > 1:
		assert stimulus.shape[1:] == receptive_field.shape[2:], (
			'Stimulus and receptive field must have the same spatial dimensions'
		)
	assert stimulus.shape[0] >= receptive_field.shape[0], (
		'Stimulus length must be greater than receptive field length'
	)

	# Ensure arrays are correctly shaped
	if stimulus.ndim == 1:
		stimulus = stimulus[:, np.newaxis]
	if receptive_field.ndim == 2:
		receptive_field = receptive_field[:, :, np.newaxis]

	T, K = stimulus.shape[0], receptive_field.shape[0]

	# Make design matrix
	t_idx = np.arange(T)
	k_idx = np.arange(K)
	X = stimulus[t_idx[:, None] - k_idx]  # (T, K, *spatial_dims)
	X[t_idx[:, None] < k_idx] = 0  # Zero out invalid indices

	# Make receptive field matrix
	receptive_field = receptive_field[::-1, ...]
	rf_matrix = np.transpose(
		receptive_field, (0, *range(2, receptive_field.ndim), 1)
	)  # shape (K, *spatial, N)

	# Multiply to get output
	result = np.tensordot(
		X, rf_matrix, axes=(range(1, X.ndim), range(0, rf_matrix.ndim - 1))
	)

	return result


# INCOMPLETE IMPLEMENTATION
def receptive_field(stimulus, activity, kernel_size):
	"""Computes the receptive field kernel that maps stimulus to activity.

	This function inverts the encoder function by finding the optimal receptive field
	that transforms the stimulus into the given neural activity via a linear mapping.

	Args:
		stimulus: numpy.ndarray
			Input stimulus with shape:
			- axis 0: time/samples (T)
			- axis [1:]: spatial dimensions (optional)
		activity: numpy.ndarray
			Neural activity with shape:
			- axis 0: time/samples (T) (must match stimulus)
			- axis 1: number of neurons (N)
		kernel_size: int
			Temporal size of the receptive field kernel (K)
		regularization: float
			Regularization parameter for ridge regression (lambda)

	Returns:
		numpy.ndarray:
			Estimated receptive field kernel with shape:
			- axis 0: kernel timepoints (K)
			- axis 1: number of neurons (N) from activity
			- axis [2:]: spatial dimensions from stimulus
	"""

	assert activity.ndim == 2, 'Activity must be a 2D array with shape (T, N)'
	assert stimulus.shape[0] == activity.shape[0], (
		'Stimulus and activity must have the same time dimension'
	)
	assert kernel_size <= stimulus.shape[0], (
		'Kernel size must be less than the stimulus length'
	)
	assert (
		isinstance(kernel_size, (int, np.integer, float))
		and float(kernel_size).is_integer()
	), (
		'Kernel size must be an integer or a float/NumPy integer that can be cast to an integer'
	)

	T, K, N, spatial_dims = (
		stimulus.shape[0],
		kernel_size,
		activity.shape[1],
		stimulus.shape[1:],
	)
	D = int(np.prod(spatial_dims))

	# Make design matrix
	t_idx = np.arange(T)
	k_idx = np.arange(K)
	X = stimulus[t_idx[:, None] - k_idx]  # (T, K, *spatial_dims)
	X[t_idx[:, None] < k_idx] = 0  # Zero out invalid indices
	X = X[:, ::-1, ...]  # Reverse the kernel axis
	X = X.reshape(T, K, D)

	def one_n_naive(X, activity):
		X_flattened = X.reshape(T, K * D)  # (T, K * D)
		X_cov = np.dot(X_flattened.T, X_flattened)  # (K * D, K * D)
		X_inv = np.linalg.pinv(X_cov)  # (K * D, K * D)
		correlated = np.dot(X_flattened.T, activity)  # (T, K)
		output = np.dot(X_inv, correlated)  # (K)
		output_reshaped = output.reshape(K, *spatial_dims)  # (K, *spatial_dims)
		return output_reshaped

	rf = np.zeros((K, N, *spatial_dims))
	for n in range(N):
		rf[:, n, ...] = one_n_naive(X, activity[:, n])
	rf = rf.reshape(K, N, *spatial_dims)

	return rf
