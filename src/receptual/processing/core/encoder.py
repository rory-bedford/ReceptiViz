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
			- axis [1:]: spatial dimensions

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

	Notes:
		We treat this as the application of a weight matrix found by
		linear regression to the stimulus:

		Y = X*W

		Where Y is an output matrix of shape (T, N), X is the design matrix
		of shape (T, K*spatial_dims), and W is the receptive field kernel
		of shape (K*spatial_dims,N).

	Usage:
		>> activity = encoder(stimulus, receptive_field)
	"""

	assert stimulus.ndim >= 2, 'Stimulus must be at least a 2D array'
	assert receptive_field.ndim >= 3, 'Receptive field must be at least a 3D array'
	assert stimulus.ndim + 1 == receptive_field.ndim, (
		'Dimensions of arrays are not compatible'
	)
	assert stimulus.shape[1:] == receptive_field.shape[2:], (
		'Stimulus and receptive field must have the same spatial dimensions'
	)
	assert stimulus.shape[0] >= receptive_field.shape[0], (
		'Stimulus length must be greater than receptive field length'
	)

	T, K = stimulus.shape[0], receptive_field.shape[0]

	# Make design matrix #
	######################
	# This is a (T by K*D) matrix consisting of all input features where
	# each feature is the time-shifted version of the previous feature
	t_idx = np.arange(T)
	k_idx = np.arange(K)
	X = stimulus[t_idx[:, None] - k_idx]  # (T, K, *spatial_dims)
	X[t_idx[:, None] < k_idx] = 0  # Zero out invalid indices

	# Multiply by receptive field #
	###############################
	# This is Y = X*W
	receptive_field = receptive_field[::-1, ...]  # Shape: (K, N, *spatial_dims)
	receptive_field = np.transpose(
		receptive_field, (0, *range(2, receptive_field.ndim), 1)
	)  # Shape: (K, *spatial, N)
	activity = np.tensordot(
		X, receptive_field, axes=(range(1, X.ndim), range(0, receptive_field.ndim - 1))
	)  # Shape: (T, N)

	return activity


def receptive_field(stimulus, activity, kernel_size):
	"""Computes the receptive field kernel that maps stimulus to activity.

	This function inverts the encoder function by finding the optimal receptive field
	that transforms the stimulus into the given neural activity via a linear mapping.

	Args:
		stimulus: numpy.ndarray
			Input stimulus with shape:

			- axis 0: time/samples (T)
			- axis [1:]: spatial dimensions

		activity: numpy.ndarray
			Neural activity with shape:

			- axis 0: time/samples (T) (must match stimulus)
			- axis 1: number of neurons (N)

		kernel_size: int
			Temporal size of the receptive field kernel (K)

	Returns:
		numpy.ndarray:
			Estimated receptive field kernel with shape:

			- axis 0: kernel timepoints (K)
			- axis 1: number of neurons (N) from activity
			- axis [2:]: spatial dimensions from stimulus

	Notes:
		We treat this as the solution of a linear regression problem where the
		stimulus makes up the design matrix, activity is the target output,
		and the receptive field is the weight matrix:

		W = (X^T * X)^-1 * (X^T * Y)

		Where Y is an output matrix of shape (T, N), X is the design matrix
		of shape (T, K*spatial_dims), and W is the receptive field kernel
		of shape (K*spatial_dims,N).

	Usage:
		>> receptive_field = receptive_field(stimulus, activity, kernel_size)
	"""

	assert stimulus.ndim >= 2, 'Stimulus must be at least a 2D array'
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

	# Make design matrix #
	######################
	# This is a (T by K*D) matrix consisting of all input features where
	# each feature is the time-shifted version of the previous feature
	stimulus = stimulus.reshape(T, D)  # Shape: (T, D)
	t_idx = np.arange(T)
	k_idx = np.arange(K)
	X = stimulus[t_idx[:, None] - k_idx]  # Shape: (T, K, D)
	X[t_idx[:, None] < k_idx] = 0  # Zero out invalid indices
	X = X[:, ::-1, ...]  # Reverse the kernel axis
	X = X.reshape(T, K * D)  # Shape: (T, K * D)

	# Compute decorrelated receptive field #
	########################################
	# This is W = (X^T * X)^-1 * (X^T * Y)
	X_cov = np.dot(X.T, X)  # Shape: (K * D, K * D)
	X_inv = np.linalg.pinv(X_cov)  # Shape: (K * D, K * D)
	correlated = np.tensordot(X, activity, (0, 0))  # Shape (K * D, N)
	rf = np.dot(X_inv, correlated)  # Shape: (K * D, N)

	# Reshape to original dimensions
	rf = rf.reshape(K, D, N)  # Shape: (K, D, N)
	rf = rf.transpose(0, 2, 1)  # Shape: (K, N, D)
	rf = rf.reshape(K, N, *spatial_dims)  # Shape: (K, N, *spatial_dims)

	return rf
