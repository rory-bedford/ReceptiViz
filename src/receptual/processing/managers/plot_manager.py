import numpy as np

MAX_RANGE = 1000


class PlotManager:
	"""A class to manage data for the plotting widget.

	Attributes:
		name (str): The name of the data type.
		data (np.ndarray): The data to be plotted.
		slice_data (np.ndarray): The slice of the data acted on by range selectors
		ndim (int): The number of dimensions of the data.
		shape (tuple): The shape of the data.
		available_axes (list): List of available axes for selection.
		selected_axes (list): List of currently selected axes.
		slice_axes (list): List of axes that can be sliced.
		ranges (dict): Dictionary to store ranges for each axis.
		slices (dict): Dictionary to store slices for each axis.
		plot_data (np.ndarray): The data that will be plotted after applying slices and ranges.
	"""

	def __init__(self, manager):
		self.name: str = manager.name
		assert self.name in ['Receptive Field', 'Activity', 'Stimulus'], (
			f"Invalid name: {self.name}. Must be one of ['Receptive Field', 'Activity', 'Stimulus']."
		)
		self.normalize_data(manager.data)
		self.ndim: int = self.data.ndim
		self.shape: tuple = self.data.shape

		self.available_axes = [i for i in range(self.ndim)]

		if self.name == 'Receptive Field':
			self.axis_names = {
				0: 'Kernel',
				1: 'Neuron',
				**{i: f'Dim {i - 1}' for i in range(2, self.ndim)},
			}
		elif self.name == 'Activity':
			self.axis_names = {0: 'Time', 1: 'Neuron'}
		elif self.name == 'Stimulus':
			self.axis_names = {
				0: 'Time',
				**{i: f'Dim {i}' for i in range(1, self.ndim)},
			}

		# Fixed
		self.shape = {i: (0, self.data.shape[i]) for i in range(self.ndim)}

		# Dynamic - change as user interacts with the widget
		if self.name == 'Activity':
			self.update_axes([0, 1])  # Default to first two axes
		elif self.name == 'Stimulus':
			if self.ndim >= 3:
				self.update_axes([1, 2])
			else:
				self.update_axes([0, 1])
		elif self.name == 'Receptive Field':
			if self.ndim >= 4:
				self.update_axes([2, 3])
			else:
				self.update_axes([0, 2])

	def update_ranges(self, axis, min_val, max_val):
		"""Update the range for a given axis."""
		assert axis in self.selected_axes, f'Axis {axis} is not available.'
		assert min_val <= max_val, 'Minimum value must be less than maximum value.'
		assert min_val >= self.shape[axis][0] and max_val <= self.shape[axis][1], (
			'Range values must be within the data shape.'
		)
		self.ranges[axis] = (min_val, max_val)
		self.update_plot_data()

	def update_slice(self, axis, value):
		"""Update the slice for a given axis."""
		assert axis in self.slice_axes, f'Axis {axis} is not available.'
		assert value >= self.shape[axis][0] and value < self.shape[axis][1], (
			'Slice value must be within the data shape.'
		)
		self.slices[axis] = value
		self.update_plot_data()

	def update_plot_data(self):
		"""Update the array that gets plotted based on selected slices and ranges."""
		transpose_order = self.selected_axes + self.slice_axes
		plot_data = np.transpose(self.data, axes=transpose_order)
		slices = []
		for axis in transpose_order:
			if axis in self.selected_axes:
				slices.append(slice(self.ranges[axis][0], self.ranges[axis][1] + 1))
			elif axis in self.slice_axes:
				slices.append(self.slices[axis])
		self.plot_data = plot_data[tuple(slices)]

	def update_axes(self, axes):
		"""Update the selected axes and ranges based on the provided axes."""
		assert len(axes) == 2, 'Exactly two axes must be selected.'
		self.selected_axes = axes
		self.slice_axes = [i for i in range(self.ndim) if i not in self.selected_axes]
		self.ranges = {
			i: [0, min(self.data.shape[i] - 1, MAX_RANGE)] for i in self.selected_axes
		}
		self.slices = {i: 0 for i in self.slice_axes}
		self.update_plot_data()

	def normalize_data(self, data):
		"""Normalize new data, assign it, and update the plot data."""

		# Replace invalid values
		if np.isnan(data).any() or np.isinf(data).any():
			data[np.isnan(data)] = 0
			data[np.isinf(data)] = 0

		# Normalize to range 0-1
		min_val = np.min(data)
		max_val = np.max(data)
		if min_val != max_val:
			data = (data - min_val) / (max_val - min_val)

		# Scale to reasonable height for 3D view
		data = data * 15

		self.data = data
		self.ndim = self.data.ndim
		self.shape = self.data.shape
