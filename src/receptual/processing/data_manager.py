import numpy as np
from receptual.processing.utils.data_utils import load_numpy_array
import receptual

MIN_TIME_POINTS = 10


class EncoderDataManager:
	"""
	Handles loading, validating, and processing data for the encoder tab.

	Attributes:
		- activity: Neural activity data
		- stimulus: Stimulus data
		- receptive_field: Receptive field data
		- activity_info: Information about the activity data
		- stimulus_info: Information about the stimulus data
		- receptive_field_info: Information about the receptive field data
		- sample_rate: Sample rate for the data
		- errors: List of validation errors
	"""

	def __init__(self):
		self.reset_state()

	def reset_state(self):
		"""
		Reset all state variables to their default values.

		Returns:
			EncoderDataManager: Self
		"""
		self.activity = None
		self.stimulus = None
		self.receptive_field = None

		self.errors = []

		self.activity_info = {
			'name': 'Activity',
			'unit': 'Hz',
			'timestamps': None,
			'no_neurons': None,
			'status': None,
		}

		self.stimulus_info = {
			'name': 'Stimulus',
			'unit': 'n/a',
			'timestamps': None,
			'spatial_dims': None,
			'status': None,
		}

		self.receptive_field_info = {
			'name': 'Receptive Field',
			'unit': 'n/a',
			'kernel_size': None,
			'no_neurons': None,
			'spatial_dims': None,
			'status': None,
		}

		self.sample_rate = None

		return self

	def set_sample_rate(self, sample_rate):
		"""
		Set the sample rate for the data manager.

		Args:
			sample_rate: Sample rate in Hz
		"""
		if sample_rate <= 0:
			raise ValueError('Sample rate must be positive')
		self.sample_rate = float(sample_rate)
		return self

	def get_time_axis(self, n_samples):
		"""Get time axis values for the given number of samples"""
		if self.sample_rate is None:
			return np.arange(n_samples)
		else:
			return np.arange(n_samples) / self.sample_rate

	def set_activity(self, file_path):
		"""
		Load neural activity data from file.

		If stimulus data already exists, automatically computes
		and validates the receptive field using receptual.receptive_field.

		Args:
			file_path: Path to the activity data file

		Returns:
			bool: True if loading was successful, False otherwise
		"""
		assert self.receptive_field is None, (
			'Cannot set activity data when receptive field is already set'
		)
		try:
			data = load_numpy_array(file_path)
			if self._validate_activity(data):
				self.activity = data
				self.activity_info['timestamps'] = data.shape[0]
				self.activity_info['no_neurons'] = data.shape[1]
				self.activity_info['status'] = 'loaded'

				if self.stimulus is not None:
					try:
						computed_receptive_field = receptual.receptive_field(
							self.stimulus, data
						)
						self.set_receptive_field(computed_receptive_field)
						self.receptive_field_info['status'] = 'computed'
					except Exception as e:
						self.errors.append(
							f'Failed to compute receptive field: {str(e)}'
						)

				return True
			return False
		except Exception as e:
			self.errors.append(f'Error loading activity data: {str(e)}')
			return False

	def set_stimulus(self, file_path):
		"""
		Load stimulus data from file.

		Args:
			file_path: Path to the stimulus data file

		Returns:
			bool: True if loading was successful, False otherwise
		"""
		try:
			data = load_numpy_array(file_path)
			if self._validate_stimulus(data):
				self.stimulus = data
				self.stimulus_info['dimensions'] = data.shape
				self.stimulus_info['status'] = 'loaded'
				return True
			return False
		except Exception as e:
			self.errors.append(f'Error loading stimulus data: {str(e)}')
			return False

	def set_receptive_field(self, file_path):
		"""
		Load receptive field data from file.

		If stimulus data already exists, automatically computes
		and validates the activity using receptual.encoder.

		Args:
			file_path: Path to the receptive field data file

		Returns:
			bool: True if loading was successful, False otherwise
		"""
		try:
			data = load_numpy_array(file_path)
			if self._validate_receptive_field(data):
				self.receptive_field = data
				self.receptive_field_info['dimensions'] = data.shape
				self.receptive_field_info['status'] = 'loaded'
				if self.stimulus is not None:
					try:
						computed_activity = receptual.encoder(self.stimulus, data)
						self.set_activity(computed_activity)
						self.activity_info['status'] = 'computed'
					except Exception as e:
						self.errors.append(f'Failed to compute activity: {str(e)}')

				return True
			return False
		except Exception as e:
			self.errors.append(f'Error loading receptive field data: {str(e)}')
			return False

	def _validate_activity(self, data):
		"""
		Validate activity data format and dimensions.

		Activity should be a 2D array with time points as first dimension.
		If stimulus exists, activity time points must match stimulus time points.
		If receptive field exists, activity dimension 2 must match receptive field dimension 2.

		Args:
			data: Activity data array to validate

		Returns:
			bool: True if data is valid, False otherwise
		"""
		if not isinstance(data, np.ndarray):
			self.errors.append('Activity data must be a numpy array')
			return False

		if data.ndim != 2:
			self.errors.append(
				f'Activity data must be 2D (time x neurons), got {data.ndim}D'
			)
			return False

		if data.shape[0] < MIN_TIME_POINTS:
			self.errors.append(
				f'Not enough time points in activity data: {data.shape[0]} < {MIN_TIME_POINTS}'
			)
			return False

		if self.stimulus is not None:
			if data.shape[0] != self.stimulus.shape[0]:
				self.errors.append(
					f'Activity time points ({data.shape[0]}) must match stimulus time points ({self.stimulus.shape[0]})'
				)
				return False

		if self.receptive_field is not None and self.receptive_field.ndim >= 2:
			if data.shape[1] != self.receptive_field.shape[1]:
				self.errors.append(
					f'Activity neuron count ({data.shape[1]}) must match receptive field second dimension ({self.receptive_field.shape[1]})'
				)
				return False

		return True

	def _validate_stimulus(self, data):
		"""
		Validate stimulus data format and dimensions.

		Stimulus should be at least a 2D array with time points as first dimension.
		If activity exists, stimulus time points must match activity time points.
		If receptive field exists, stimulus spatial dimensions must match receptive field spatial dimensions.

		Args:
			data: Stimulus data array to validate

		Returns:
			bool: True if data is valid, False otherwise
		"""
		if not isinstance(data, np.ndarray):
			self.errors.append('Stimulus data must be a numpy array')
			return False

		if data.ndim < 2:
			self.errors.append(
				f'Stimulus data must have at least 2 dimensions, got {data.ndim}D'
			)
			return False

		if data.shape[0] < MIN_TIME_POINTS:
			self.errors.append(
				f'Not enough time points in stimulus data: {data.shape[0]} < {MIN_TIME_POINTS}'
			)
			return False

		if self.activity is not None:
			if data.shape[0] != self.activity.shape[0]:
				self.errors.append(
					f'Stimulus time points ({data.shape[0]}) must match activity time points ({self.activity.shape[0]})'
				)
				return False

		if self.receptive_field is not None:
			stim_spatial_dims = data.shape[1:]
			receptive_field_spatial_dims = self.receptive_field.shape[2:]

			if stim_spatial_dims != receptive_field_spatial_dims:
				self.errors.append(
					f'Stimulus spatial dimensions {stim_spatial_dims} must match receptive field spatial dimensions {receptive_field_spatial_dims}'
				)
				return False

		return True

	def _validate_receptive_field(self, data):
		"""
		Validate receptive field data format and dimensions.

		Receptive field should be a numpy array with appropriate dimensions.
		If activity exists, receptive field dimension 1 must match activity dimension 1 (neuron count).
		If stimulus exists, receptive field spatial dimensions (2+) must match stimulus spatial dimensions (1+).

		Args:
			data: Receptive field data array to validate

		Returns:
			bool: True if data is valid, False otherwise
		"""
		if not isinstance(data, np.ndarray):
			self.errors.append('Receptive field data must be a numpy array')
			return False

		if self.activity is not None:
			if data.shape[1] != self.activity.shape[1]:
				self.errors.append(
					f'Receptive field neuron dimension ({data.shape[1]}) must match activity neuron count ({self.activity.shape[1]})'
				)
				return False

		if self.stimulus is not None:
			stim_spatial_dims = self.stimulus.shape[1:]
			receptive_field_spatial_dims = data.shape[2:]

			if receptive_field_spatial_dims != stim_spatial_dims:
				self.errors.append(
					f'Receptive field spatial dimensions {receptive_field_spatial_dims} must match stimulus spatial dimensions {stim_spatial_dims}'
				)
				return False

		return True
