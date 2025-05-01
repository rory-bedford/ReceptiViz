import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer


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
		self.plot_frame = None
		self.checkbox_container = None

		# Store camera parameters to maintain view during updates
		self.last_distance = None
		self.last_elevation = None
		self.last_azimuth = None
		self.last_center = None

		# Rotation properties
		self.rotation_timer = QTimer(self)
		self.rotation_timer.timeout.connect(self.rotate_model)
		self.rotation_speed = 1  # degrees per frame
		self.is_rotating = False

		self.init_ui()

	def init_ui(self):
		"""Initialize the UI components"""
		# Create main layout
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)  # Remove spacing between components

		# Create error label (hidden by default)
		self.error_label = QLabel(' ')
		self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.error_label.setStyleSheet(
			'color: white; background-color: black; padding: 20px;'
		)
		layout.addWidget(self.error_label)

		# Create a frame with the light grey border - now with thinner border
		plot_frame = QFrame()
		plot_frame.setFrameShape(QFrame.Shape.StyledPanel)  # Add panel style
		plot_frame.setStyleSheet('border: 0.5px solid #cccccc;')  # Thinner border

		# Use a layout for the frame
		plot_frame_layout = QVBoxLayout(plot_frame)
		plot_frame_layout.setContentsMargins(0, 0, 0, 0)  # No margins
		plot_frame_layout.setSpacing(0)  # No spacing

		# Create the GL view widget
		self.plot_view = CustomGLViewWidget(self)
		self.plot_view.setBackgroundColor('k')  # Black background
		self.plot_view.setCameraPosition(distance=40, elevation=30, azimuth=45)

		# Add the plot view to the frame layout
		plot_frame_layout.addWidget(self.plot_view)

		# Add the frame to the main layout
		layout.addWidget(plot_frame, 1)  # Stretch factor of 1

		# Create the rotation checkbox with proper event handling
		self.rotation_checkbox = QCheckBox('Rotate')
		self.rotation_checkbox.setChecked(False)
		self.rotation_checkbox.toggled.connect(self.toggle_rotation)

		# Style the checkbox - make sure it's visible and clickable
		self.rotation_checkbox.setStyleSheet("""
			QCheckBox {
				color: white;
				background-color: rgba(40, 40, 40, 150); 
				border-radius: 3px;
				padding: 3px;
				margin: 5px;
			}
			QCheckBox::indicator {
				width: 13px;
				height: 13px;
			}
		""")

		# Add checkbox directly to the main layout
		from PyQt6.QtWidgets import QWidget

		# Create a container widget for the checkbox that overlays on top of the plot
		checkbox_container = QWidget(self)
		checkbox_container.setAttribute(
			Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
		)

		# Use a horizontal layout with a stretch to push the checkbox to the right
		checkbox_layout = QHBoxLayout(checkbox_container)
		checkbox_layout.setContentsMargins(0, 0, 5, 5)  # Small right and bottom margin
		checkbox_layout.addStretch(1)  # Push to the right
		checkbox_layout.addWidget(self.rotation_checkbox)

		# Set the container to be on top of everything
		checkbox_container.raise_()

		# Position the container at the bottom of the plot
		from PyQt6.QtCore import QPoint, QSize

		def update_container_position():
			if plot_frame.isVisible():
				# Position at the bottom right of the plot frame
				pos = plot_frame.mapTo(
					self, QPoint(0, plot_frame.height() - checkbox_container.height())
				)
				size = QSize(plot_frame.width(), checkbox_container.sizeHint().height())
				checkbox_container.setGeometry(
					pos.x(), pos.y(), size.width(), size.height()
				)

		# Call update whenever the plot frame changes size or visibility
		old_resize_event = plot_frame.resizeEvent

		def new_resize_event(event):
			if old_resize_event:
				old_resize_event(event)
			update_container_position()

		plot_frame.resizeEvent = new_resize_event

		# Initialize the position
		update_container_position()

		# Set default camera parameters
		self.last_distance = 40
		self.last_elevation = 30
		self.last_azimuth = 45
		self.last_center = [0, 0, 0]

		# Hide the plot frame initially until we have data
		plot_frame.hide()
		self.error_label.show()
		checkbox_container.hide()  # Hide checkbox container too

		# Store the frame and checkbox container for later visibility control
		self.plot_frame = plot_frame
		self.checkbox_container = checkbox_container

		# Store the update position function
		self.update_container_position = update_container_position

		# Update the widget with initial data
		self.update_plot()

	def toggle_rotation(self, checked):
		"""Toggle rotation animation on/off"""
		self.is_rotating = checked
		if checked:
			# Start the rotation timer
			self.rotation_timer.start(30)  # ~33 fps
		else:
			self.rotation_timer.stop()

	def rotate_model(self):
		"""Rotate the view around by adjusting the camera azimuth"""
		if self.plot_view and self.plot_view.isVisible():
			# Get current camera parameters
			opts = self.plot_view.opts

			# Update azimuth (horizontal rotation)
			current_azimuth = opts['azimuth']
			new_azimuth = (current_azimuth + self.rotation_speed) % 360

			# Update the camera position with the new azimuth
			# Note: this keeps all other camera parameters (distance, elevation, center) unchanged
			self.plot_view.setCameraPosition(azimuth=new_azimuth)

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

	def restore_camera_position(self):
		"""Restore the previously saved camera position"""
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

	def set_plot_manager(self, plot_manager):
		"""Set the plot manager and update the plot"""
		self.plot_manager = plot_manager
		self.update_plot()

	def update_plot(self):
		"""Update the plot with current data from the plot manager"""
		# Save rotation state
		was_rotating = self.is_rotating
		if was_rotating:
			self.toggle_rotation(False)

		# Reset grid_plot
		self.grid_plot = None

		# Save current camera position before updating
		if self.plot_view is not None and self.plot_view.isVisible():
			self.save_camera_position()

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

		# Check if we have a valid plot manager with data
		if self.plot_manager is None or not hasattr(self.plot_manager, 'plot_data'):
			self.plot_frame.hide()  # Hide the frame
			self.checkbox_container.hide()  # Hide the checkbox container
			self.error_label.setText(' ')
			self.error_label.show()
			return

		try:
			# Get the data
			data = self.plot_manager.plot_data

			# Check data shape and validity
			if data is None or data.size == 0:
				self.plot_frame.hide()  # Hide the frame
				self.checkbox_container.hide()  # Hide the checkbox container
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

			# Process the data
			normalized_data = data  # Data is already normalized by the plot manager

			# Special case for neuron data
			if show_as_lines:
				# Determine which axis is the neuron axis
				neuron_index = self.plot_manager.selected_axes.index(neuron_axis)

				# Determine number of neurons and time/dimension size
				if neuron_index == 0:  # Neurons are along rows (first axis)
					n_neurons = normalized_data.shape[0]
					time_size = normalized_data.shape[1]

					# Calculate center points for better positioning
					time_center = time_size / 2
					neuron_center = (n_neurons * 5) / 2

					# Create a line for each neuron
					for i in range(n_neurons):
						# Get data for this neuron
						y_values = normalized_data[i, :]
						x_values = np.arange(time_size)

						# Create points array for this neuron
						points = np.empty((len(x_values), 3))
						points[:, 0] = x_values - time_center  # Center X coordinates
						points[:, 1] = (i * 5) - neuron_center  # Center Y coordinates
						points[:, 2] = y_values  # Z coordinate (activity height)

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

					# Set camera position appropriate for neuron plots
					data_size = max(n_neurons * 5, time_size)

				elif neuron_index == 1:  # Neurons are along columns (second axis)
					time_size = normalized_data.shape[0]
					n_neurons = normalized_data.shape[1]

					# Calculate center points for better positioning
					time_center = time_size / 2
					neuron_center = (n_neurons * 5) / 2

					# Create a line for each neuron
					for i in range(n_neurons):
						# Get data for this neuron
						y_values = normalized_data[:, i]
						x_values = np.arange(time_size)

						# Create points array for this neuron
						points = np.empty((len(x_values), 3))
						points[:, 0] = x_values - time_center  # Center X coordinates
						points[:, 1] = (i * 5) - neuron_center  # Center Y coordinates
						points[:, 2] = y_values  # Z coordinate (activity height)

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

					# Set camera position appropriate for neuron plots
					data_size = max(n_neurons * 5, time_size)

				# Set reasonable camera distance if needed
				if not self.plot_view.isVisible() or None in [
					self.last_distance,
					self.last_elevation,
					self.last_azimuth,
				]:
					self.plot_view.setCameraPosition(
						distance=data_size * 1.5, elevation=30, azimuth=45
					)

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
			self.restore_camera_position()

			# Show the plot and hide the error
			self.plot_frame.show()
			self.checkbox_container.show()
			self.update_container_position()  # Make sure the container is positioned correctly
			self.error_label.hide()

		except Exception as e:
			self.plot_frame.hide()
			self.checkbox_container.hide()
			self.error_label.setText(f'Error plotting data: {str(e)}')
			self.error_label.show()
			raise

		# Restart rotation if it was active before
		if was_rotating:
			self.toggle_rotation(True)
