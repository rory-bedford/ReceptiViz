import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class CustomGLViewWidget(gl.GLViewWidget):
	"""Extended GLViewWidget that captures mouse events to save camera position"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.parent_widget = parent

	def mouseReleaseEvent(self, ev):
		"""Override to capture mouse release events"""
		# Call the parent class implementation first
		super().mouseReleaseEvent(ev)

		# Now notify our parent to save the camera position
		if hasattr(self.parent_widget, 'save_camera_position'):
			self.parent_widget.save_camera_position()


class Plot3DWidget(QWidget):
	"""A 3D plotting widget using PyQtGraph's OpenGL capabilities."""

	def __init__(self, plot_manager=None, parent=None):
		super().__init__(parent)
		self.plot_manager = plot_manager

		# Initialize OpenGL plot
		self.plot_view = None
		self.grid_plot = None
		self.error_label = None

		# Store camera parameters to maintain view during updates
		self.last_distance = None
		self.last_elevation = None
		self.last_azimuth = None
		self.last_center = None

		self.init_ui()

	def init_ui(self):
		"""Initialize the UI components"""
		# Create layout
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)

		# Create error label (hidden by default)
		self.error_label = QLabel(' ')
		self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.error_label.setStyleSheet(
			'color: white; background-color: black; padding: 20px;'
		)
		layout.addWidget(self.error_label)

		# Create the custom OpenGL view widget that passes mouse events
		self.plot_view = CustomGLViewWidget(self)
		self.plot_view.setBackgroundColor('k')  # Black background
		self.plot_view.setCameraPosition(distance=40, elevation=30, azimuth=45)
		layout.addWidget(self.plot_view)

		# Set default camera parameters
		self.last_distance = 40
		self.last_elevation = 30
		self.last_azimuth = 45
		self.last_center = [0, 0, 0]

		# Hide the view initially until we have data
		self.plot_view.hide()
		self.error_label.show()

		# Update the widget with initial data
		self.update_plot()

	def save_camera_position(self):
		"""Save the current camera position parameters"""
		try:
			# Get the current camera state
			opts = self.plot_view.opts

			# Save the parameters
			self.last_distance = opts['distance']
			self.last_elevation = opts['elevation']
			self.last_azimuth = opts['azimuth']
			self.last_center = opts['center']
		except Exception:
			# Silent error handling - no print statements
			pass

	def set_plot_manager(self, plot_manager):
		"""Set the plot manager and update the plot"""
		self.plot_manager = plot_manager
		self.update_plot()

	def update_plot(self):
		"""Update the plot with current data from the plot manager"""
		if self.plot_manager is not None:
			print('dad')
			print(self.plot_manager.plot_data.shape)
		# Save current camera position before updating
		if self.plot_view is not None and self.plot_view.isVisible():
			self.save_camera_position()

		# Check if we need to clean up any existing plots
		# We need special handling since there could be multiple items
		# for neuron plots or a single grid_plot for surface plots

		# Clear all items from the view to ensure clean start
		if self.plot_view is not None:
			# Make a copy of the items list since we'll be modifying it
			items_to_remove = self.plot_view.items.copy()
			for item in items_to_remove:
				try:
					self.plot_view.removeItem(item)
				except Exception:
					# Silently ignore errors during cleanup
					pass

		# Reset grid_plot
		self.grid_plot = None

		# Check if we have a valid plot manager with data
		if self.plot_manager is None or not hasattr(self.plot_manager, 'plot_data'):
			self.plot_view.hide()
			self.error_label.setText(' ')
			self.error_label.show()
			return

		try:
			# Get the data
			data = self.plot_manager.plot_data

			# Check data shape and validity
			if data is None or data.size == 0:
				self.plot_view.hide()
				self.error_label.setText(' ')
				self.error_label.show()
				return

			# Check if one of the selected axes is 'Neurons'
			neuron_axis = None
			show_as_lines = False

			if hasattr(self.plot_manager, 'selected_axes') and hasattr(
				self.plot_manager, 'axis_names'
			):
				for axis_idx in self.plot_manager.selected_axes:
					if self.plot_manager.axis_names.get(axis_idx, '') == 'Neuron':
						neuron_axis = axis_idx
						show_as_lines = True
						break

			# Check if the data has any dimension of size 1
			has_single_dim = False
			original_shape = data.shape
			if len(data.shape) == 2 and 1 in data.shape:
				has_single_dim = True

			# Process the data - no normalization needed since it's been done in the plot processor
			normalized_data = data  # Direct use - data is already normalized

			# Special case for neuron data or 1D data
			if show_as_lines or has_single_dim:
				if has_single_dim:
					# Handle single dimension case as before
					if original_shape[0] == 1:  # Row vector
						# Get the raw 1D data
						y_values = data[0, :]
						x_values = np.arange(len(y_values))

						# Create connected points for line plot
						points = np.empty((len(x_values), 3))
						points[:, 0] = x_values  # X coordinate
						points[:, 1] = np.zeros(
							len(x_values)
						)  # Y coordinate (fixed at 0)
						points[:, 2] = normalized_data[
							0, :
						]  # Z coordinate (normalized height)

						# Create the line plot with the line_strip mode
						self.grid_plot = gl.GLLinePlotItem(
							pos=points,
							color=(1, 1, 1, 1),  # White
							width=4,  # Thicker line for better visibility
							antialias=True,  # Smooth the line
							mode='line_strip',  # Connect points in sequence
						)

						# Center the plot
						self.grid_plot.translate(-len(y_values) / 2, 0, 0)

					elif original_shape[1] == 1:  # Column vector
						# Get the raw 1D data
						y_values = data[:, 0]
						x_values = np.arange(len(y_values))

						# Create connected points for the line plot
						points = np.empty((len(x_values), 3))
						points[:, 0] = np.zeros(
							len(x_values)
						)  # X coordinate (fixed at 0)
						points[:, 1] = x_values  # Y coordinate
						points[:, 2] = normalized_data[
							:, 0
						]  # Z coordinate (normalized height)

						# Create the line plot with the line_strip mode
						self.grid_plot = gl.GLLinePlotItem(
							pos=points,
							color=(1, 1, 1, 1),  # White
							width=4,  # Thicker line for better visibility
							antialias=True,  # Smooth the line
							mode='line_strip',  # Connect points in sequence
						)

						# Center the plot
						self.grid_plot.translate(0, -len(y_values) / 2, 0)

				elif show_as_lines:
					# We have neuron data that should be displayed as multiple line plots

					# Determine which axis is the neuron axis (0 or 1)
					neuron_index = self.plot_manager.selected_axes.index(neuron_axis)

					# Create a group to hold all line plots
					self.grid_plot = gl.GLViewWidget()

					# Set background color to match main widget
					self.grid_plot.setBackgroundColor((0, 0, 0, 0))  # Transparent

					# Determine number of neurons and non-neuron dimension size
					if neuron_index == 0:  # Neurons are along rows (first axis)
						n_neurons = normalized_data.shape[0]
						other_dim_size = normalized_data.shape[1]

						# Create a line for each neuron
						for i in range(n_neurons):
							# Get data for this neuron
							y_values = normalized_data[i, :]
							x_values = np.arange(other_dim_size)

							# Create points array for this neuron
							points = np.empty((len(x_values), 3))
							points[:, 0] = x_values  # X coordinate
							points[:, 1] = (
								i * 1.5
							)  # Y coordinate offset by neuron index
							points[:, 2] = y_values  # Z coordinate (normalized height)

							# Create line plot for this neuron
							line = gl.GLLinePlotItem(
								pos=points,
								color=(1, 1, 1, 1),  # White
								width=2,  # Line width
								antialias=True,  # Smooth line
								mode='line_strip',  # Connect points in sequence
							)

							# Add to main view
							self.plot_view.addItem(line)

						# Set appropriate camera parameters for neuron plots
						if not self.plot_view.isVisible() or None in [
							self.last_distance,
							self.last_elevation,
							self.last_azimuth,
						]:
							self.plot_view.setCameraPosition(
								distance=max(n_neurons, other_dim_size) * 2,
								elevation=30,
								azimuth=45,
							)

					else:  # Neurons are along columns (second axis)
						n_neurons = normalized_data.shape[1]
						other_dim_size = normalized_data.shape[0]

						# Create a line for each neuron
						for i in range(n_neurons):
							# Get data for this neuron
							y_values = normalized_data[:, i]
							x_values = np.arange(other_dim_size)
							x_values -= x_values[
								len(x_values) // 2
							]  # Center x values around 0

							# Create points array for this neuron
							points = np.empty((len(x_values), 3))
							points[:, 0] = x_values  # X coordinate
							points[:, 1] = i * 5  # Y coordinate offset by neuron index
							points[:, 2] = y_values  # Z coordinate (normalized height)

							# Create line plot for this neuron
							line = gl.GLLinePlotItem(
								pos=points,
								color=(1, 1, 1, 1),  # White
								width=2,  # Line width
								antialias=True,  # Smooth line
								mode='line_strip',  # Connect points in sequence
							)

							# Add to main view
							self.plot_view.addItem(line)

						# Set appropriate camera parameters for neuron plots
						if not self.plot_view.isVisible() or None in [
							self.last_distance,
							self.last_elevation,
							self.last_azimuth,
						]:
							self.plot_view.setCameraPosition(
								distance=max(n_neurons, other_dim_size) * 2,
								elevation=30,
								azimuth=45,
							)

					# Restore saved camera position if available
					if self.plot_view.isVisible() and None not in [
						self.last_distance,
						self.last_elevation,
						self.last_azimuth,
					]:
						try:
							self.plot_view.setCameraPosition(
								distance=self.last_distance,
								elevation=self.last_elevation,
								azimuth=self.last_azimuth,
								pos=self.last_center,
							)
						except Exception:
							# Silent error handling
							self.plot_view.setCameraPosition(
								distance=self.last_distance,
								elevation=self.last_elevation,
								azimuth=self.last_azimuth,
							)

					# Show the plot view and hide the error
					self.plot_view.show()
					self.error_label.hide()

			else:
				# Normal 2D surface plot for regular data
				self.grid_plot = gl.GLSurfacePlotItem(
					z=normalized_data,
					shader='shaded',
					color=(1, 1, 1, 1),  # White color
					drawEdges=True,  # Draw edges to create grid effect
					drawFaces=False,  # Don't draw faces to keep it wireframe
					glOptions='opaque',
				)

				# Center the plot at the origin
				data_x_size, data_y_size = normalized_data.shape
				self.grid_plot.translate(-data_x_size / 2, -data_y_size / 2, 0)

				# Add the plot to the view
				self.plot_view.addItem(self.grid_plot)

				# Set camera position based on data dimensions
				if not self.plot_view.isVisible() or None in [
					self.last_distance,
					self.last_elevation,
					self.last_azimuth,
				]:
					data_size = max(normalized_data.shape[0], normalized_data.shape[1])
					self.plot_view.setCameraPosition(
						distance=data_size * 1.5, elevation=30, azimuth=45
					)

				# Restore saved camera position if available
				if self.plot_view.isVisible() and None not in [
					self.last_distance,
					self.last_elevation,
					self.last_azimuth,
				]:
					try:
						self.plot_view.setCameraPosition(
							distance=self.last_distance,
							elevation=self.last_elevation,
							azimuth=self.last_azimuth,
							pos=self.last_center,
						)
					except Exception:
						# Silent error handling
						self.plot_view.setCameraPosition(
							distance=self.last_distance,
							elevation=self.last_elevation,
							azimuth=self.last_azimuth,
						)

				# Show the plot view and hide the error
				self.plot_view.show()
				self.error_label.hide()

		except Exception as e:
			# If there's an error, show the error message in UI but don't print to console
			self.plot_view.hide()
			self.error_label.setText(f'Error plotting data: {str(e)}')
			self.error_label.show()
			# Raise the exception again for higher-level handling
			raise
