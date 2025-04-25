from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QGroupBox,
	QPushButton,
	QGridLayout,
)
from PyQt6.QtCore import pyqtSignal, Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QLinearGradient


class AxisSelector(QWidget):
	"""Widget for selecting two axes for plotting multi-dimensional data."""

	axis_selected = pyqtSignal(list)  # Signal emits a list of selected axis indices

	def __init__(self, plot_manager=None, parent=None):
		super().__init__(parent)
		self.plot_manager = plot_manager
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(0, 0, 0, 0)

		# Create group box for axis selection - will be populated when plot_manager is set
		self.axis_group = QGroupBox()
		self.axis_layout = QVBoxLayout(self.axis_group)

		# Add to main layout
		self.main_layout.addWidget(self.axis_group)

		# Set initial state based on plot_manager availability
		if not plot_manager:
			self.set_blank_state()
		else:
			self.init_ui()

	def set_blank_state(self):
		"""Set widget to completely blank state."""
		# Hide the group box completely
		self.axis_group.hide()

		# Clear any previous UI elements
		while self.axis_layout.count():
			item = self.axis_layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()

	def init_ui(self):
		"""Initialize the UI components with actual controls."""
		# Show the group box
		self.axis_group.show()
		self.axis_group.setTitle('Select Axes for Plotting')

		# Clear any previous UI elements
		while self.axis_layout.count():
			item = self.axis_layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()

			# Create a single horizontal layout for everything
		main_controls_layout = QHBoxLayout()

		# Create left-side layout for axis selection
		axis_selection_layout = QHBoxLayout()

		# Header label
		header_label = QLabel('Select axes:')
		axis_selection_layout.addWidget(header_label)

		# First axis combo
		self.x_axis_label = QLabel('X-Axis:')
		axis_selection_layout.addWidget(self.x_axis_label)

		self.x_axis_combo = QComboBox()
		axis_selection_layout.addWidget(self.x_axis_combo)

		# Second axis combo
		self.y_axis_label = QLabel('Y-Axis:')
		axis_selection_layout.addWidget(self.y_axis_label)

		self.y_axis_combo = QComboBox()
		axis_selection_layout.addWidget(self.y_axis_combo)

		# Add the axis selection layout to the main controls layout
		main_controls_layout.addLayout(axis_selection_layout)

		# Add spacer to push the apply button to the right
		main_controls_layout.addStretch(1)

		# Create Apply button
		self.apply_button = QPushButton('Apply')
		self.apply_button.clicked.connect(self.apply_axis_selection)
		self.apply_button.setFixedWidth(80)  # Set a fixed width for the button
		main_controls_layout.addWidget(self.apply_button)

		# Add the main controls layout to the axis layout
		self.axis_layout.addLayout(main_controls_layout)

		# Update with available options
		self.update_axis_options()

	def set_plot_manager(self, plot_manager):
		"""Set or update the plot manager and refresh the UI"""
		self.plot_manager = plot_manager
		if plot_manager:
			self.init_ui()
		else:
			self.set_blank_state()

	def update_axis_options(self):
		"""Update the combo boxes with available axes from the plot manager"""
		if not hasattr(self, 'x_axis_combo') or not self.plot_manager:
			return

		# Clear existing items
		self.x_axis_combo.clear()
		self.y_axis_combo.clear()

		# Add available axes to combo boxes
		for axis in self.plot_manager.available_axes:
			axis_name = self.plot_manager.axis_names.get(axis, f'Axis {axis}')
			axis_label = f'{axis_name} (Axis {axis})'

			self.x_axis_combo.addItem(axis_label, axis)
			self.y_axis_combo.addItem(axis_label, axis)

		# Set default selections based on plot_manager.selected_axes
		if (
			hasattr(self.plot_manager, 'selected_axes')
			and len(self.plot_manager.selected_axes) >= 2
		):
			x_axis_index = self.x_axis_combo.findData(
				self.plot_manager.selected_axes[0]
			)
			y_axis_index = self.y_axis_combo.findData(
				self.plot_manager.selected_axes[1]
			)

			if x_axis_index >= 0:
				self.x_axis_combo.setCurrentIndex(x_axis_index)
			if y_axis_index >= 0:
				self.y_axis_combo.setCurrentIndex(y_axis_index)
		# Otherwise select the first two axes
		elif self.x_axis_combo.count() >= 2:
			self.x_axis_combo.setCurrentIndex(0)
			self.y_axis_combo.setCurrentIndex(1)

	def apply_axis_selection(self):
		"""Apply the selected axes and emit the axis_selected signal"""
		if not self.plot_manager:
			return

		# Get selected axis indices
		x_axis = self.x_axis_combo.currentData()
		y_axis = self.y_axis_combo.currentData()

		# Ensure two different axes are selected
		if x_axis == y_axis:
			from PyQt6.QtWidgets import QMessageBox

			QMessageBox.warning(
				self,
				'Invalid Selection',
				'Please select two different axes for plotting.',
			)
			return

		# Update plot manager with selected axes
		selected_axes = [x_axis, y_axis]

		# Update plot manager
		if hasattr(self.plot_manager, 'update_axes'):
			self.plot_manager.update_axes(selected_axes)

		# Emit signal with selected axes
		self.axis_selected.emit(selected_axes)


class RangeSlider(QWidget):
	"""A custom slider widget that allows selection of a range between min and max values."""

	range_changed = pyqtSignal(int, int)  # (min_value, max_value)

	def __init__(
		self, min_value=0, max_value=100, lower_value=0, upper_value=100, parent=None
	):
		super().__init__(parent)

		self.min_value = min_value
		self.max_value = max_value
		self.lower_value = max(min_value, lower_value)
		self.upper_value = min(max_value, upper_value)

		self.pressed_control = None
		self.hover_control = None
		self.lower_pos = 0
		self.upper_pos = 0
		self.offset = 0
		self.position = 0
		self.last_click_pos = None

		# Set minimal height for the slider
		self.setMinimumHeight(30)

		# Handle Size
		self.handle_width = 12
		self.handle_height = 25

		self.setMinimumWidth(200)  # Wider default for better UX
		self.setMouseTracking(True)

		# No layout or labels needed - just a pure graphical widget
		self.update_position()

	def update_position(self):
		"""Update the position of the slider controls based on current values"""
		span = self.max_value - self.min_value
		if span == 0:
			self.lower_pos = 0
			self.upper_pos = 0
			return

		available_width = self.width() - (2 * self.handle_width)
		self.lower_pos = (
			self.handle_width
			+ available_width * (self.lower_value - self.min_value) / span
		)
		self.upper_pos = (
			self.handle_width
			+ available_width * (self.upper_value - self.min_value) / span
		)

		self.update()

	def set_range(self, min_value, max_value):
		"""Set the range of the slider"""
		self.min_value = min_value
		self.max_value = max_value

		# Ensure values are within the new range
		self.set_lower_value(max(min_value, self.lower_value))
		self.set_upper_value(min(max_value, self.upper_value))

	def set_lower_value(self, value):
		"""Set the lower value of the range"""
		value = max(self.min_value, min(value, self.upper_value))
		if value != self.lower_value:
			self.lower_value = value
			self.update_position()
			self.range_changed.emit(self.lower_value, self.upper_value)

	def set_upper_value(self, value):
		"""Set the upper value of the range"""
		value = max(self.lower_value, min(value, self.max_value))
		if value != self.upper_value:
			self.upper_value = value
			self.update_position()
			self.range_changed.emit(self.lower_value, self.upper_value)

	def paintEvent(self, event):
		"""Paint the slider and its handles"""
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Center the slider vertically
		track_y = self.height() // 2

		# Draw track - full width of widget
		track_rect = QRect(
			self.handle_width, track_y - 3, self.width() - 2 * self.handle_width, 6
		)
		track_brush = QBrush(QColor(200, 200, 200))
		painter.fillRect(track_rect, track_brush)

		# Draw selected range
		selected_rect = QRect(
			int(self.lower_pos), track_y - 3, int(self.upper_pos - self.lower_pos), 6
		)
		selected_brush = QBrush(QColor(0, 120, 215))
		painter.fillRect(selected_rect, selected_brush)

		# Draw handles
		lower_handle = QRect(
			int(self.lower_pos - self.handle_width // 2),
			track_y - self.handle_height // 2,
			self.handle_width,
			self.handle_height,
		)
		upper_handle = QRect(
			int(self.upper_pos - self.handle_width // 2),
			track_y - self.handle_height // 2,
			self.handle_width,
			self.handle_height,
		)

		# Draw with gradient
		gradient = QLinearGradient(
			0, track_y - self.handle_height // 2, 0, track_y + self.handle_height // 2
		)
		gradient.setColorAt(0, QColor(240, 240, 240))
		gradient.setColorAt(1, QColor(210, 210, 210))

		# Fill handles with gradient
		painter.setBrush(gradient)
		painter.setPen(QColor(150, 150, 150))
		painter.drawRoundedRect(lower_handle, 3, 3)
		painter.drawRoundedRect(upper_handle, 3, 3)

		# Optionally draw small dots or tick marks to indicate min and max values
		# at the ends of the track

		# Min dot
		min_dot_x = self.handle_width
		painter.setBrush(QBrush(QColor(100, 100, 100)))
		painter.drawEllipse(min_dot_x - 2, track_y - 2, 4, 4)

		# Max dot
		max_dot_x = self.width() - self.handle_width
		painter.drawEllipse(max_dot_x - 2, track_y - 2, 4, 4)

	def resizeEvent(self, event):
		"""Update positions when widget is resized"""
		super().resizeEvent(event)
		self.update_position()

	def mousePressEvent(self, event):
		"""Handle mouse press events"""
		if event.button() == Qt.MouseButton.LeftButton:
			self.last_click_pos = event.position().x()
			track_y = self.height() // 2

			# Check if a handle was clicked - more generous hit area
			lower_handle = QRect(
				int(self.lower_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			upper_handle = QRect(
				int(self.upper_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			if lower_handle.contains(
				int(event.position().x()), int(event.position().y())
			):
				self.pressed_control = 'lower'
				self.offset = event.position().x() - self.lower_pos
				# Set cursor to indicate dragging
				self.setCursor(Qt.CursorShape.SizeHorCursor)
			elif upper_handle.contains(
				int(event.position().x()), int(event.position().y())
			):
				self.pressed_control = 'upper'
				self.offset = event.position().x() - self.upper_pos
				# Set cursor to indicate dragging
				self.setCursor(Qt.CursorShape.SizeHorCursor)
			else:
				# Check if clicked on track - jump to position
				track_rect = QRect(
					self.handle_width,
					track_y - 10,
					self.width() - 2 * self.handle_width,
					20,
				)

				if track_rect.contains(
					int(event.position().x()), int(event.position().y())
				):
					# Find which handle is closer to click position
					if abs(event.position().x() - self.lower_pos) < abs(
						event.position().x() - self.upper_pos
					):
						self.pressed_control = 'lower'
						self.offset = 0
					else:
						self.pressed_control = 'upper'
						self.offset = 0

					# Directly move the handle to the click position
					self.mouseMoveEvent(event)
				else:
					self.pressed_control = None

	def mouseMoveEvent(self, event):
		"""Handle mouse move events"""
		if self.pressed_control == 'lower':
			pos = event.position().x() - self.offset
			span = self.max_value - self.min_value
			new_value = self.min_value + (pos - self.handle_width) * span / (
				self.width() - 2 * self.handle_width
			)
			self.set_lower_value(int(new_value))
		elif self.pressed_control == 'upper':
			pos = event.position().x() - self.offset
			span = self.max_value - self.min_value
			new_value = self.min_value + (pos - self.handle_width) * span / (
				self.width() - 2 * self.handle_width
			)
			self.set_upper_value(int(new_value))
		elif not self.pressed_control:
			# Update cursor if hovering over a handle
			track_y = self.height() // 2
			lower_handle = QRect(
				int(self.lower_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			upper_handle = QRect(
				int(self.upper_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			if lower_handle.contains(
				int(event.position().x()), int(event.position().y())
			) or upper_handle.contains(
				int(event.position().x()), int(event.position().y())
			):
				self.setCursor(Qt.CursorShape.SizeHorCursor)
			else:
				self.setCursor(Qt.CursorShape.ArrowCursor)

	def mouseReleaseEvent(self, event):
		"""Handle mouse release events"""
		self.pressed_control = None
		self.setCursor(Qt.CursorShape.ArrowCursor)


class SliceSelector(QWidget):
	"""A custom slider for selecting a single slice of data"""

	slice_changed = pyqtSignal(int)

	def __init__(self, min_value=0, max_value=100, value=0, parent=None):
		super().__init__(parent)

		self.min_value = min_value
		self.max_value = max_value
		self.value = max(min_value, min(value, max_value))

		self.setMinimumHeight(30)
		self.setMinimumWidth(200)
		self.setMouseTracking(True)

		self.handle_pos = 0
		self.pressed = False
		self.handle_width = 12
		self.handle_height = 25

		# No layout or labels needed - just a pure graphical widget
		self.update_handle_position()

	def update_handle_position(self):
		"""Update handle position based on current value"""
		span = self.max_value - self.min_value
		if span == 0:
			self.handle_pos = 0
			return

		available_width = self.width() - (2 * self.handle_width)
		self.handle_pos = (
			self.handle_width + available_width * (self.value - self.min_value) / span
		)
		self.update()

	def set_range(self, min_value, max_value):
		"""Set the range of the slider"""
		self.min_value = min_value
		self.max_value = max_value

		# Ensure value is within the new range
		self.set_value(max(min_value, min(self.value, max_value)))

	def set_value(self, value):
		"""Set the slider value"""
		value = max(self.min_value, min(value, self.max_value))
		if value != self.value:
			self.value = value
			self.update_handle_position()
			self.slice_changed.emit(self.value)

	def paintEvent(self, event):
		"""Draw the slider and handle"""
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Center the slider vertically
		track_y = self.height() // 2

		# Draw track - full width of widget
		track_rect = QRect(
			self.handle_width, track_y - 3, self.width() - 2 * self.handle_width, 6
		)
		track_brush = QBrush(QColor(200, 200, 200))
		painter.fillRect(track_rect, track_brush)

		# Draw handle
		handle_rect = QRect(
			int(self.handle_pos - self.handle_width // 2),
			track_y - self.handle_height // 2,
			self.handle_width,
			self.handle_height,
		)

		# Draw with gradient
		gradient = QLinearGradient(
			0, track_y - self.handle_height // 2, 0, track_y + self.handle_height // 2
		)
		gradient.setColorAt(0, QColor(240, 240, 240))
		gradient.setColorAt(1, QColor(210, 210, 210))

		# Fill handle with gradient
		painter.setBrush(gradient)
		painter.setPen(QColor(150, 150, 150))
		painter.drawRoundedRect(handle_rect, 3, 3)

		# Optionally draw small dots or tick marks at the ends of the track
		# Min dot
		min_dot_x = self.handle_width
		painter.setBrush(QBrush(QColor(100, 100, 100)))
		painter.drawEllipse(min_dot_x - 2, track_y - 2, 4, 4)

		# Max dot
		max_dot_x = self.width() - self.handle_width
		painter.drawEllipse(max_dot_x - 2, track_y - 2, 4, 4)

	def resizeEvent(self, event):
		"""Update positions when widget is resized"""
		super().resizeEvent(event)
		self.update_handle_position()

	def mousePressEvent(self, event):
		"""Handle mouse press events"""
		if event.button() == Qt.MouseButton.LeftButton:
			track_y = self.height() // 2

			# Check if handle was clicked
			handle_rect = QRect(
				int(self.handle_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			if handle_rect.contains(
				int(event.position().x()), int(event.position().y())
			):
				self.pressed = True
				# Set cursor to indicate dragging
				self.setCursor(Qt.CursorShape.SizeHorCursor)
			else:
				# Check if clicked on track - jump to position
				track_rect = QRect(
					self.handle_width,
					track_y - 10,
					self.width() - 2 * self.handle_width,
					20,
				)

				if track_rect.contains(
					int(event.position().x()), int(event.position().y())
				):
					self.pressed = True
					# Move handle directly to click position
					self.mouseMoveEvent(event)

	def mouseMoveEvent(self, event):
		"""Handle mouse move events"""
		if self.pressed:
			# Calculate new value based on position
			pos = event.position().x()
			span = self.max_value - self.min_value
			new_value = self.min_value + (pos - self.handle_width) * span / (
				self.width() - 2 * self.handle_width
			)
			self.set_value(int(new_value))
		else:
			# Update cursor if hovering over handle
			track_y = self.height() // 2
			handle_rect = QRect(
				int(self.handle_pos - self.handle_width),
				track_y - self.handle_height // 2 - 5,
				2 * self.handle_width,
				self.handle_height + 10,
			)

			if handle_rect.contains(
				int(event.position().x()), int(event.position().y())
			):
				self.setCursor(Qt.CursorShape.SizeHorCursor)
			else:
				self.setCursor(Qt.CursorShape.ArrowCursor)

	def mouseReleaseEvent(self, event):
		"""Handle mouse release events"""
		self.pressed = False
		self.setCursor(Qt.CursorShape.ArrowCursor)


class RangeSelector(QWidget):
	"""A widget for selecting data ranges and slices for plotting."""

	# Add signals for plot updates
	range_changed = pyqtSignal()  # Signal when any range value changes
	slice_changed = pyqtSignal()  # Signal when any slice value changes

	def __init__(self, plot_manager=None, parent=None):
		super().__init__(parent)
		self.plot_manager = plot_manager
		self.range_sliders = {}  # Sliders for selected axes
		self.slice_selectors = {}  # Sliders for non-selected axes
		self.value_labels = {}  # Labels showing current values/ranges

		# Main layout for the widget
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(0, 0, 0, 0)

		# Create a group box for range selection
		self.range_group = QGroupBox()
		self.range_layout = QGridLayout(self.range_group)
		self.range_layout.setColumnStretch(1, 1)  # Give the slider column stretch

		self.main_layout.addWidget(self.range_group)

		# Set initial state based on plot_manager availability
		if not plot_manager:
			self.set_blank_state()
		else:
			self.init_ui()

	def set_blank_state(self):
		"""Set widget to completely blank state."""
		# Hide the group box completely
		self.range_group.hide()

		# Clear any previous widgets from the layout
		self.clear_widgets()

	def init_ui(self):
		"""Initialize the UI with range selectors and sliders."""
		# Show group box and set title
		self.range_group.show()
		self.range_group.setTitle('Data Range Selection')

		# Update widgets based on plot manager
		self.update_widgets()

	def set_plot_manager(self, plot_manager):
		"""Set the plot manager and update the UI"""
		self.plot_manager = plot_manager
		if plot_manager:
			self.init_ui()
		else:
			self.set_blank_state()

	def update_widgets(self):
		"""Update all widgets based on the current plot manager state"""
		# Clear existing widgets
		self.clear_widgets()

		if not self.plot_manager:
			self.set_blank_state()
			return

		# Create range sliders for selected axes
		row = 0

		# Check if there are selected axes
		if (
			hasattr(self.plot_manager, 'selected_axes')
			and self.plot_manager.selected_axes
		):
			for axis in self.plot_manager.selected_axes:
				row = self.create_range_slider(axis, row)

		# Check if there are slice axes
		if hasattr(self.plot_manager, 'slice_axes') and self.plot_manager.slice_axes:
			for axis in self.plot_manager.slice_axes:
				row = self.create_slice_selector(axis, row)

	def clear_widgets(self):
		"""Clear all widgets from the layout"""
		# Remove all widgets from the layout
		while self.range_layout.count() > 0:
			item = self.range_layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()

		# Clear our references to UI components
		self.range_sliders.clear()
		self.slice_selectors.clear()
		self.value_labels.clear()

	def create_range_slider(self, axis, row):
		"""Create a range slider for a selected axis"""
		# Get axis name for label
		axis_name = self.plot_manager.axis_names.get(axis, f'Axis {axis}')

		# Create a widget for the axis name and value to stack vertically
		axis_widget = QWidget()
		axis_layout = QVBoxLayout(axis_widget)
		axis_layout.setContentsMargins(0, 0, 0, 0)
		axis_layout.setSpacing(1)  # Tight spacing

		# Label with axis name
		name_label = QLabel(f'{axis_name}:')
		name_label.setStyleSheet('font-weight: bold;')  # Make it stand out
		axis_layout.addWidget(name_label)

		# Get current range values
		min_val = self.plot_manager.shape[axis][0]
		max_val = self.plot_manager.shape[axis][1] - 1
		lower_val, upper_val = self.plot_manager.ranges.get(axis, (min_val, max_val))

		# Value label to show current range
		value_label = QLabel(f'Range: [{lower_val}, {upper_val}]')
		value_label.setStyleSheet('color: #666; font-size: 10pt;')  # Subtle appearance
		axis_layout.addWidget(value_label)

		# Store the value label for later updates
		self.value_labels[axis] = value_label

		# Check if there's actually a range to select (more than one value)
		if min_val >= max_val:
			# Only one possible value, use a simple centered label
			fixed_text = QLabel(f'Fixed at {min_val}')
			fixed_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
			fixed_text.setStyleSheet(
				'color: #999; font-style: italic;'
			)  # Subtle, italicized text

			# Add widgets to grid layout
			self.range_layout.addWidget(
				axis_widget, row, 0, 1, 1, Qt.AlignmentFlag.AlignTop
			)
			self.range_layout.addWidget(fixed_text, row, 1)

			# Store the static label in place of the slider (we won't need to update it)
			self.range_sliders[axis] = None
		else:
			# Normal case - create a slider
			slider = RangeSlider(min_val, max_val, lower_val, upper_val)

			# Connect slider to update function
			slider.range_changed.connect(
				lambda min_val, max_val, axis=axis: self.on_range_changed(
					axis, min_val, max_val
				)
			)

			# Add widgets to grid layout
			self.range_layout.addWidget(
				axis_widget, row, 0, 1, 1, Qt.AlignmentFlag.AlignTop
			)
			self.range_layout.addWidget(slider, row, 1)

			# Store slider for future reference
			self.range_sliders[axis] = slider

		return row + 1  # Return next row index

	def create_slice_selector(self, axis, row):
		"""Create a slice selector for a non-selected axis"""
		# Get axis name for label
		axis_name = self.plot_manager.axis_names.get(axis, f'Axis {axis}')

		# Create a widget for the axis name and value to stack vertically
		axis_widget = QWidget()
		axis_layout = QVBoxLayout(axis_widget)
		axis_layout.setContentsMargins(0, 0, 0, 0)
		axis_layout.setSpacing(1)  # Tight spacing

		# Label with axis name
		name_label = QLabel(f'{axis_name} Slice:')
		name_label.setStyleSheet('font-weight: bold;')  # Make it stand out
		axis_layout.addWidget(name_label)

		# Get current slice value
		min_val = self.plot_manager.shape[axis][0]
		max_val = self.plot_manager.shape[axis][1] - 1
		current_val = self.plot_manager.slices.get(axis, min_val)

		# Value label to show current slice
		value_label = QLabel(f'Value: {current_val}')
		value_label.setStyleSheet('color: #666; font-size: 10pt;')  # Subtle appearance
		axis_layout.addWidget(value_label)

		# Store the value label for later updates
		self.value_labels[axis] = value_label

		# Check if there's actually a range to select (more than one value)
		if min_val >= max_val:
			# Only one possible value, use a simple centered label
			fixed_text = QLabel(f'Fixed at {min_val}')
			fixed_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
			fixed_text.setStyleSheet(
				'color: #999; font-style: italic;'
			)  # Subtle, italicized text

			# Add widgets to grid layout
			self.range_layout.addWidget(
				axis_widget, row, 0, 1, 1, Qt.AlignmentFlag.AlignTop
			)
			self.range_layout.addWidget(fixed_text, row, 1)

			# Store the static label in place of the slider (we won't need to update it)
			self.slice_selectors[axis] = None

			# Update the plot manager directly with this fixed value
			if hasattr(self.plot_manager, 'update_slice'):
				self.plot_manager.update_slice(axis, min_val)
		else:
			# Normal case - create a selector
			selector = SliceSelector(min_val, max_val, current_val)

			# Connect to update function
			selector.slice_changed.connect(
				lambda value, axis=axis: self.on_slice_changed(axis, value)
			)

			# Add to layout
			self.range_layout.addWidget(
				axis_widget, row, 0, 1, 1, Qt.AlignmentFlag.AlignTop
			)
			self.range_layout.addWidget(selector, row, 1)

			# Store for future reference
			self.slice_selectors[axis] = selector

		return row + 1  # Return next row index

	def on_range_changed(self, axis, min_val, max_val):
		"""Handle changes to the range slider"""
		if not self.plot_manager:
			return

		if hasattr(self.plot_manager, 'update_ranges'):
			self.plot_manager.update_ranges(axis, min_val, max_val)

			# Update the value label
			if axis in self.value_labels:
				self.value_labels[axis].setText(f'Range: [{min_val}, {max_val}]')

			# Emit signal that a range has changed - for plot updating
			self.range_changed.emit()

	def on_slice_changed(self, axis, value):
		"""Handle changes to the slice selector"""
		if not self.plot_manager:
			return

		if hasattr(self.plot_manager, 'update_slice'):
			self.plot_manager.update_slice(axis, value)

			# Update the value label
			if axis in self.value_labels:
				self.value_labels[axis].setText(f'Value: {value}')

			# Emit signal that a slice has changed - for plot updating
			self.slice_changed.emit()
