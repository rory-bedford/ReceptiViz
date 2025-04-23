import numpy as np
from pathlib import Path
from receptual.processing.utils.data_utils import load_numpy_array
import receptual

MIN_TIME_POINTS = 10
DEFAULT_KERNEL_SIZE = 1


class EncoderDataManager:
	"""Handles loading, validating, and processing data for the encoder tab.

	This class manages interactions between activity, stimulus and receptive field data,
	providing validation and automatic computation when possible.

	Attributes:
		activity: Neural activity data.
		stimulus: Stimulus data.
		receptive_field: Receptive field data.
		sample_rate: Sample rate for the data.
	"""

	def __init__(self):
		self.activity = Activity(self)
		self.stimulus = Stimulus(self)
		self.receptive_field = ReceptiveField(self)
		self.sample_rate = None

	def set_sample_rate(self, sample_rate):
		"""Set the sample rate for the data manager.

		Args:
			sample_rate: Sample rate in Hz.

		Returns:
			self: The data manager instance.

		Raises:
			ValueError: If sample rate is not positive.
		"""
		if sample_rate <= 0:
			raise ValueError('Sample rate must be positive')
		self.sample_rate = float(sample_rate)
		return self


class ReceptiveField:
	"""Class for handling receptive field data.

	This class manages loading, validating, and processing receptive field data,
	as well as tracking relationships with activity and stimulus data.
	"""

	def __init__(self, data_manager):
		self.data_manager = data_manager
		self.reset_state()

	def reset_state(self):
		"""Reset all state variables to their default values.

		If activity was computed from this receptive field, also resets activity.
		"""
		self.data: np.ndarray = None
		self.errors: list = []
		self.name: str = 'Receptive Field'
		self.unit: str = None
		self.kernel_size: int = DEFAULT_KERNEL_SIZE
		self.no_neurons: int = None
		self.spatial_dims: tuple = None
		self.computed: bool = False
		self.loaded: bool = False
		self.filepath: Path = None
		self.available: bool = True

		if hasattr(self.data_manager, 'activity'):
			if self.data_manager.activity.computed:
				self.data_manager.activity.reset_state()
			if not self.data_manager.activity.loaded:
				self.data_manager.activity.available = True
			else:
				self.available = False

	def validate_data(self, file_path):
		"""Validate receptive field data format and dimensions.

		Receptive field should be a numpy array with appropriate dimensions.
		If activity exists, receptive field dimension 1 must match activity dimension 1 (neuron count).
		If stimulus exists, receptive field spatial dimensions (2+) must match stimulus spatial dimensions (1+).

		Args:
			file_path: Path to the receptive field data file.

		Returns:
			np.ndarray or None: The data array if valid, None otherwise.
		"""
		try:
			data = load_numpy_array(file_path)
		except Exception as e:
			self.errors.append(f'Error loading receptive field data: {str(e)}')
			return None

		if not isinstance(data, np.ndarray):
			self.errors.append('Receptive field data must be a numpy array')
			return None

		if self.data_manager.activity.loaded:
			if data.shape[1] != self.data_manager.activity.no_neurons:
				self.errors.append(
					f'Receptive field neuron dimension ({data.shape[1]}) must match activity neuron count ({self.data_manager.activity.no_neurons})'
				)
				return None

		if self.data_manager.stimulus.loaded:
			receptive_field_spatial_dims = data.shape[2:]

			if receptive_field_spatial_dims != self.data_manager.stimulus.spatial_dims:
				self.errors.append(
					f'Receptive field spatial dimensions {receptive_field_spatial_dims} must match stimulus spatial dimensions {self.data_manager.stimulus.spatial_dims}'
				)
				return None

		return data

	def set_data(self, file_path):
		"""Load receptive field data from file.

		If stimulus data already exists, automatically computes
		and validates the activity using receptual.encoder.

		Args:
			file_path: Path to the receptive field data file.

		Returns:
			bool: True if loading was successful, False otherwise.
		"""
		if self.data_manager.activity.loaded:
			self.errors.append(
				'Cannot set receptive field data when activity is already set'
			)
			return False

		data = self.validate_data(file_path)
		if data is not None:
			self.data = data
			self.kernel_size = data.shape[0]
			self.no_neurons = data.shape[1]
			self.spatial_dims = data.shape[2:]
			self.loaded = True
			self.filepath = Path(file_path)
			self.available = False
			self.data_manager.activity.available = False
			if self.data_manager.stimulus.loaded:
				try:
					computed_activity = receptual.encoder(
						self.data_manager.stimulus.data, data
					)
					self.data_manager.activity.set_data(computed_activity)
					self.data_manager.activity.computed = True
				except Exception as e:
					self.errors.append(f'Failed to compute activity: {str(e)}')
					self.reset_state()
					return False

			return True
		else:
			self.reset_state()
			return False

	def update_kernel_size(self, kernel_size):
		"""Update the kernel size for the receptive field.

		Args:
			kernel_size: New kernel size.

		Raises:
			ValueError: If kernel size is not positive.
		"""
		assert self.computed, (
			'Kernel size can only be updated if receptive field is computed'
		)
		if kernel_size <= 0:
			raise ValueError('Kernel size must be positive')
		self.kernel_size = int(kernel_size)
		self.data = receptual.receptive_field(
			self.data_manager.stimulus.data,
			self.data_manager.activity.data,
			kernel_size=self.kernel_size,
		)


class Stimulus:
	"""Class for handling stimulus data.

	This class manages loading, validating, and processing stimulus data,
	as well as tracking relationships with activity and receptive field data.
	"""

	def __init__(self, data_manager):
		self.data_manager = data_manager
		self.reset_state()

	def reset_state(self):
		"""Reset all state variables to their default values.

		If activity or receptive field was computed from this stimulus, also resets them.
		"""
		self.data: np.ndarray = None
		self.errors: list = []
		self.name: str = 'Stimulus'
		self.unit: str = None
		self.timestamps: int = None
		self.spatial_dims: tuple = None
		self.loaded: bool = False
		self.filepath: Path = None
		self.available: bool = True

		if (
			hasattr(self.data_manager, 'activity')
			and self.data_manager.activity.computed
		):
			self.data_manager.activity.reset_state()
		if (
			hasattr(self.data_manager, 'receptive_field')
			and self.data_manager.receptive_field.computed
		):
			self.data_manager.receptive_field.reset_state()

	def validate_data(self, file_path):
		"""Validate stimulus data format and dimensions.

		Stimulus should be at least a 2D array with time points as first dimension.
		If activity exists, stimulus time points must match activity time points.
		If receptive field exists, stimulus spatial dimensions must match receptive field spatial dimensions.

		Args:
			file_path: Path to the stimulus data file.

		Returns:
			np.ndarray or None: The data array if valid, None otherwise.
		"""
		try:
			data = load_numpy_array(file_path)
		except Exception as e:
			self.errors.append(f'Error loading stimulus data: {str(e)}')
			return None

		if not isinstance(data, np.ndarray):
			self.errors.append('Stimulus data must be a numpy array')
			return None

		if data.ndim < 3:
			self.errors.append(
				f'Stimulus data must have at least 3 dimensions, got {data.ndim}D'
			)
			return None

		if data.shape[0] < MIN_TIME_POINTS:
			self.errors.append(
				f'Not enough time points in stimulus data: {data.shape[0]} < {MIN_TIME_POINTS}'
			)
			return None

		if self.data_manager.activity.loaded:
			if data.shape[0] != self.data_manager.activity.timestamps:
				self.errors.append(
					f'Stimulus time points ({data.shape[0]}) must match activity time points ({self.data_manager.activity.timestamps})'
				)
				return None

		if self.data_manager.receptive_field.loaded:
			stim_spatial_dims = data.shape[1:]

			if stim_spatial_dims != self.data_manager.receptive_field.spatial_dims:
				self.errors.append(
					f'Stimulus spatial dimensions {stim_spatial_dims} must match receptive field spatial dimensions {self.data_manager.receptive_field.spatial_dims}'
				)
				return None

		return data

	def set_data(self, file_path):
		"""Load stimulus data from file.

		If activity data exists, automatically computes and validates the
		receptive field using receptual.receptive_field.
		If receptive field exists, automatically computes activity.

		Args:
			file_path: Path to the stimulus data file.

		Returns:
			bool: True if loading was successful, False otherwise.
		"""
		data = self.validate_data(file_path)
		if data is not None:
			self.data = data
			self.spatial_dims = data.shape[1:]
			self.timestamps = data.shape[0]
			self.loaded = True
			self.filepath = Path(file_path)
			self.available = False
			if self.data_manager.activity.loaded:
				try:
					computed_receptive_field = receptual.receptive_field(
						data,
						self.data_manager.activity.data,
						kernel_size=self.data_manager.receptive_field.kernel_size,
					)
					self.data_manager.receptive_field.set_data(computed_receptive_field)
					self.data_manager.receptive_field.computed = True
				except Exception as e:
					self.errors.append(f'Failed to compute receptive field: {str(e)}')
					self.reset_state()
					return False
			elif self.data_manager.receptive_field.loaded:
				try:
					computed_activity = receptual.encoder(
						data, self.data_manager.receptive_field.data
					)
					self.data_manager.activity.set_data(computed_activity)
					self.data_manager.activity.computed = True
				except Exception as e:
					self.errors.append(f'Failed to compute activity: {str(e)}')
					self.reset_state()
					return False
			return True
		else:
			self.reset_state()
			return False


class Activity:
	"""Class for handling activity data.

	This class manages loading, validating, and processing neural activity data,
	as well as tracking relationships with stimulus and receptive field data.
	"""

	def __init__(self, data_manager):
		self.data_manager = data_manager
		self.reset_state()

	def reset_state(self):
		"""Reset all state variables to their default values.

		If receptive field was computed from this activity, also resets it.
		"""
		self.data: np.ndarray = None
		self.errors: list = []
		self.name: str = 'Activity'
		self.unit: str = None
		self.timestamps: int = None
		self.no_neurons: int = None
		self.computed: bool = False
		self.loaded: bool = False
		self.filepath: Path = None
		self.available: bool = True

		if hasattr(self.data_manager, 'receptive_field'):
			if self.data_manager.receptive_field.computed:
				self.data_manager.receptive_field.reset_state()
			if not self.data_manager.receptive_field.loaded:
				self.data_manager.receptive_field.available = True
			else:
				self.available = False

	def validate_data(self, file_path):
		"""Validate activity data format and dimensions.

		Activity should be a 2D array with time points as first dimension.
		If stimulus exists, activity time points must match stimulus time points.
		If receptive field exists, activity dimension 2 must match receptive field dimension 2.

		Args:
			file_path: Path to the activity data file.

		Returns:
			np.ndarray or None: The data array if valid, None otherwise.
		"""
		try:
			data = load_numpy_array(file_path)
		except Exception as e:
			self.errors.append(f'Error loading activity data: {str(e)}')
			return None

		if not isinstance(data, np.ndarray):
			self.errors.append('Activity data must be a numpy array')
			return None

		if data.ndim != 2:
			self.errors.append(
				f'Activity data must be 2D (time x neurons), got {data.ndim}D'
			)
			return None

		if data.shape[0] < MIN_TIME_POINTS:
			self.errors.append(
				f'Not enough time points in activity data: {data.shape[0]} < {MIN_TIME_POINTS}'
			)
			return None

		if self.data_manager.stimulus.loaded:
			if data.shape[0] != self.data_manager.stimulus.timestamps:
				self.errors.append(
					f'Activity time points ({data.shape[0]}) must match stimulus time points ({self.data_manager.stimulus.timestamps})'
				)
				return None

		if self.data_manager.receptive_field.loaded:
			if data.shape[1] != self.data_manager.receptive_field.no_neurons:
				self.errors.append(
					f'Activity neuron count ({data.shape[1]}) must match receptive field second dimension ({self.data_manager.receptive_field.no_neurons})'
				)
				return None

		return data

	def set_data(self, file_path):
		"""Load neural activity data from file, validate it, and assign it to the object.

		If stimulus data already exists, automatically computes
		and validates the receptive field using receptual.receptive_field.

		Args:
			file_path: Path to the activity data file.

		Returns:
			bool: True if loading was successful, False otherwise.
		"""
		if self.data_manager.stimulus.loaded:
			self.errors.append('Cannot set activity data when stimulus is already set')
			return False

		data = self.validate_data(file_path)
		if data is not None:
			self.data = data
			self.timestamps = data.shape[0]
			self.no_neurons = data.shape[1]
			self.loaded = True
			self.filepath = Path(file_path)
			self.available = False
			self.data_manager.receptive_field.available = False

			if self.data_manager.stimulus.loaded:
				try:
					computed_receptive_field = receptual.receptive_field(
						self.data_manager.stimulus.data, data
					)
					self.data_manager.receptive_field.set_data(computed_receptive_field)
					self.data_manager.receptive_field.computed = True
				except Exception as e:
					self.errors.append(f'Failed to compute receptive field: {str(e)}')
					self.reset_state()
					return False

			return True
		else:
			self.reset_state()
			return False
