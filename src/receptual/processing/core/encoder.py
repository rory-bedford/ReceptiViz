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
from numpy.lib.stride_tricks import sliding_window_view


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
	assert stimulus.shape[0] > receptive_field.shape[0], (
		'Stimulus length must be greater than receptive field length'
	)

	T, K = stimulus.shape[0], receptive_field.shape[0]

	result_shape = (T,) + receptive_field.shape[1:]  # Shape: (T, N, spatial_dims)
	result = np.zeros(result_shape)

	# Manual convolution calculation
	for t in range(T):
		for k in range(K):
			if t - k >= 0:
				result[t] += (
					stimulus[t - k] * receptive_field[K - 1 - k]
				)  # Will broadcast N and spatial dimensions

	if result.ndim > 2:  # Sum over spatial dimensions if they exist
		axes = tuple(range(2, result.ndim))
		result = np.sum(result, axis=axes)

	return result


# INCOMPLETE IMPLEMENTATION
def encoder_faster(stimulus, receptive_field):
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

	Notes:
		Although fast-fourier transform (FFT) convolution is faster for large arrays,
		our implementation treats this as a linear algebra problem, with T data points
		of dimension K * D, where K is the kernel size and D is total spatial
		dimensionality.
	"""

	assert stimulus.ndim + 1 == receptive_field.ndim, (
		'Dimensions of arrays are not compatible'
	)
	if stimulus.ndim > 1:
		assert stimulus.shape[1:] == receptive_field.shape[2:], (
			'Stimulus and receptive field must have the same spatial dimensions'
		)
	assert stimulus.shape[0] > receptive_field.shape[0], (
		'Stimulus length must be greater than receptive field length'
	)

	# Ensure arrays are correctly shaped
	if stimulus.ndim == 1:
		stimulus = stimulus[:, np.newaxis]
	if receptive_field.ndim == 2:
		receptive_field = receptive_field[:, :, np.newaxis]

	T, K, N = stimulus.shape[0], receptive_field.shape[0], receptive_field.shape[1]
	spatial_dims = tuple(range(2, receptive_field.ndim))
	D = np.prod(stimulus.shape[1:])

	# Pad stimulus at the beginning for causal kernel
	pad_width = ((K - 1, 0),) + ((0, 0),) * len(spatial_dims)
	stim_padded = np.pad(stimulus, pad_width, mode='constant')

	# Get sliding windows over time axis
	X = np.array(
		sliding_window_view(stim_padded, window_shape=K, axis=0)
	)  # shape: (T, *spatial_dims, K)

	# Move lag axis to the end and flatten
	X = X.reshape(T, K * D)  # design matrix of shape (T, K * D)

	# Reshape RF to shape (K * D, N)
	rf_reshaped = receptive_field.transpose(
		1, *spatial_dims, 0
	)  # shape: (N, *spatial_dims, K)
	rf_reshaped = receptive_field.reshape(N, K * D).T  # shape: (K * D, N)

	# Compute the encoded activity
	activity = X @ rf_reshaped  # shape: (T, N)

	return activity


# INCOMPLETE IMPLEMENTATION
def receptive_field(stimulus, activity, kernel_size, regularization=0):
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

	Notes:
		Our implementation of the receptive field solver decorrelates the stimulus
		to make the outputs unbiased. We artificially make this numerically stable
		with numpy's pseudo-inverse. Note that while unbiased, this solution can be
		very high variance if there are regions in frequency space not covered by
		the stimulus. Therefore, whitened stimuli are preferred where possible.
	"""

	assert activity.ndim == 2, 'Activity must be a 2D array with shape (T, N)'
	assert stimulus.shape[0] == activity.shape[0], (
		'Stimulus and activity must have the same time dimension'
	)
	assert kernel_size < stimulus.shape[0], (
		'Kernel size must be less than the stimulus length'
	)

	T, N, K = stimulus.shape[0], activity.shape[1], kernel_size

	# Center the stimulus
	stim_centered = stimulus - stimulus.mean(axis=0)

	# Change array sizes for broadcasting
	# stim_centered = np.expand_dims(stim_centered, axis=1)
	stim_centered = stim_centered[:, np.newaxis, ...]

	# Compute STA
	sta_shape = (
		K,
		N,
	) + stimulus.shape[1:]
	sta = np.zeros(sta_shape)
	for t in range(T):
		for k in range(K):
			if t - k >= 0:
				sta[-k - 1] += stim_centered[t - k] * activity[t]

	# Normalize by activity
	sta /= activity.sum(axis=0)

	print('STA shape:', sta.shape)

	# Reshape stimulus for covariance computation
	stim_2d = stim_centered.reshape(T, -1)

	# Flatten STA to shape (K*D, N)
	sta_flat = sta.reshape(kernel_size * D, -1)

	# Compute stimulus covariance
	cov = X.T @ X / X.shape[0]
	rf_flat = np.linalg.pinv(cov) @ sta_flat  # shape (K*D, N)

	# Reshape back to (K, N, ...)
	rf = rf_flat.T.reshape(activity.shape[1], kernel_size, *spatial_dims).transpose(
		1, 0, 2, 3, ...
	)
