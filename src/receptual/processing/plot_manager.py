import numpy as np


class PlotManager:
	"""A class to manage data for the plotting widget.

	Attributes:
		name (str): The name of the data type.
		data (np.ndarray): The data to be plotted.
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
		self.data: np.ndarray = manager.data
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

		# Dynamic
		self.update_axes([0, 1])  # Default to first two axes

	def update_ranges(self, axis, min_val, max_val):
		"""Update the range for a given axis."""
		assert axis in self.selected_axes, f'Axis {axis} is not available.'
		print(min_val, max_val)
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
		slices = []
		for axis in self.available_axes:
			if axis in self.selected_axes:
				slices.append(slice(self.ranges[axis][0], self.ranges[axis][1]))
			elif axis in self.slice_axes:
				slices.append(self.slices[axis])
		self.plot_data = self.data[tuple(slices)]

	def update_axes(self, axes):
		"""Update the selected axes and ranges based on the provided axes."""
		assert len(axes) == 2, 'Exactly two axes must be selected.'
		self.selected_axes = axes
		self.slice_axes = [i for i in range(self.ndim) if i not in self.selected_axes]
		self.ranges = {i: [0, self.data.shape[i] - 1] for i in self.selected_axes}
		self.slices = {i: 0 for i in self.slice_axes}
		self.update_plot_data()
