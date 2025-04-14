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
