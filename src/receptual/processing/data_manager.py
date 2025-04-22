import numpy as np
from receptual.processing.utils.data_utils import load_numpy_array
import receptual

MIN_TIME_POINTS = 10


class EncoderDataManager:
	"""
	Handles loading, validating, and processing data for the encoder tab.
	"""

	def __init__(self):
		self.reset_state()

	def reset_state(self):
		"""
		Reset all state variables to their default values.

		Returns:
			EncoderDataManager: Self for method chaining
		"""
		self.activity = None
		self.stimulus = None
		self.receptive_field = None
		self.result = None
		self.errors = []

		# Initialize all metadata in a consistent format
		self.activity_value_info = {
			'name': 'Activity',
			'unit': 'Hz',
			'dimensions': None,
			'dims': ['Time', 'Neurons'],
			'units': ['s', ''],
		}

		# Stimulus can have arbitrary dimensions (time + N spatial dimensions)
		self.stimulus_value_info = {
			'name': 'Stimulus',
			'unit': 'a.u.',
			'dimensions': None,
			'dims': [
				'Time'
			],  # Just define time dimension, others will be added based on data
			'units': ['s'],
		}

		# Receptive Field can have arbitrary dimensions
		self.receptive_field_value_info = {
			'name': 'Receptive Field',
			'unit': 'a.u.',
			'dimensions': None,
			'dims': [
				'Neurons'
			],  # Just define neurons dimension, others will be added based on data
			'units': [''],
		}

		self.sample_rate = 1.0

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

	def get_sample_rate(self):
		"""
		Get the current sample rate from the data manager.

		Returns:
			float: Sample rate in Hz
		"""
		return self.sample_rate

	def get_time_axis(self, n_samples):
		"""Get time axis values for the given number of samples"""
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
		try:
			data = load_numpy_array(file_path)
			if self.validate_activity(data):
				self.activity = data
				self.activity_value_info['dimensions'] = data.shape

				# If stimulus exists, compute receptive field
				if self.stimulus is not None:
					try:
						# Compute receptive field using receptual library
						computed_rf = receptual.receptive_field(self.stimulus, data)

						# Validate the computed receptive field
						if self.validate_receptive_field(computed_rf):
							self.receptive_field = computed_rf
							self.receptive_field_value_info['dimensions'] = (
								computed_rf.shape
							)
							self.receptive_field_value_info['name'] = (
								'Computed Receptive Field'
							)
							self.receptive_field_value_info['computed'] = True
						else:
							# Keep activity but log warning about RF computation
							self.errors.append(
								'Computed receptive field is invalid - keeping activity data only'
							)
					except Exception as e:
						# Keep activity but log warning about RF computation
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
			if self.validate_stimulus(data):
				self.stimulus = data
				self.stimulus_value_info['dimensions'] = data.shape
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
			if self.validate_receptive_field(data):
				self.receptive_field = data
				self.receptive_field_value_info['dimensions'] = data.shape

				# If stimulus exists, compute activity
				if self.stimulus is not None:
					try:
						# Compute activity using receptual library
						computed_activity = receptual.encoder(self.stimulus, data)

						# Validate the computed activity
						if self.validate_activity(computed_activity):
							self.activity = computed_activity
							self.activity_value_info['dimensions'] = (
								computed_activity.shape
							)
							self.activity_value_info['name'] = 'Computed Activity'
							self.activity_value_info['computed'] = True
						else:
							# Keep receptive field but log warning about activity computation
							self.errors.append(
								'Computed activity is invalid - keeping receptive field data only'
							)
					except Exception as e:
						# Keep receptive field but log warning about activity computation
						self.errors.append(f'Failed to compute activity: {str(e)}')

				return True
			return False
		except Exception as e:
			self.errors.append(f'Error loading receptive field data: {str(e)}')
			return False

	def validate_activity(self, data):
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

	def validate_stimulus(self, data):
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
			rf_spatial_dims = self.receptive_field.shape[2:]

			if stim_spatial_dims != rf_spatial_dims:
				self.errors.append(
					f'Stimulus spatial dimensions {stim_spatial_dims} must match receptive field spatial dimensions {rf_spatial_dims}'
				)
				return False

		return True

	def validate_receptive_field(self, data):
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
			rf_spatial_dims = data.shape[2:]

			if rf_spatial_dims != stim_spatial_dims:
				self.errors.append(
					f'Receptive field spatial dimensions {rf_spatial_dims} must match stimulus spatial dimensions {stim_spatial_dims}'
				)
				return False

		return True

	def get_errors(self):
		"""
		Get the list of accumulated validation errors.

		Returns:
			list: List of error messages
		"""
		return self.errors

	def clear_errors(self):
		"""
		Clear the list of validation errors.
		"""
		self.errors = []

	def set_dimension_info(self, array_type, dim_names=None, dim_units=None):
		"""Set dimension names and units for an array"""
		value_info = self.get_value_info(array_type)
		if value_info:
			if dim_names:
				value_info['dims'] = dim_names
			if dim_units:
				value_info['units'] = dim_units
		return self

	def get_dimension_info(self, array_type):
		"""Get dimension information for an array"""
		value_info = self.get_value_info(array_type)
		if value_info:
			return {
				'dims': value_info.get('dims', []),
				'units': value_info.get('units', []),
			}
		return None

	def set_value_info(self, array_type, value_name=None, value_unit=None):
		"""Set the name and unit for the data values"""
		value_info = self.get_value_info(array_type)
		if value_info:
			if value_name is not None:
				value_info['name'] = value_name
			if value_unit is not None:
				value_info['unit'] = value_unit
		return self

	def get_value_info(self, array_type):
		"""Get the value info dictionary for the specified array type"""
		if array_type == 'activity':
			return self.activity_value_info
		elif array_type == 'stimulus':
			return self.stimulus_value_info
		elif array_type == 'receptive_field':
			return self.receptive_field_value_info
		return None
