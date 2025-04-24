import numpy as np


class PlotManager:
	"""A class to manage data for the plotting widget."""

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

		self.selected_axes = [0, 1]
		self.slice_axes = [i for i in range(self.ndim) if i not in self.selected_axes]
		self.ranges = {0: (0, self.data.shape[0]), 1: (0, self.data.shape[1])}
		self.slices = {
			key: 0 for key in range(self.ndim) if key not in self.selected_axes
		}

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
		self.ranges = {key: (0, self.data.shape[key]) for key in range(self.ndim)}
		self.slices = {
			key: 0 for key in range(self.ndim) if key not in self.selected_axes
		}
		self.update_plot_data()
