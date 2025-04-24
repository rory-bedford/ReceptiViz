from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QGroupBox,
	QPushButton,
)
from PyQt6.QtCore import pyqtSignal


class AxisSelector(QWidget):
	"""Widget for selecting two axes for plotting multi-dimensional data.

	This widget allows users to select exactly two axes from a multi-dimensional
	array for visualization on a 2D plot.

	Attributes:
		plot_manager: The PlotManager instance containing the data to plot
		axis_selected: Signal emitted when axes are selected
	"""

	axis_selected = pyqtSignal(list)  # Signal emits a list of selected axis indices

	def __init__(self, plot_manager=None, parent=None):
		super().__init__(parent)
		self.plot_manager = plot_manager
		self.init_ui()

	def init_ui(self):
		"""Initialize the UI components"""
		main_layout = QVBoxLayout(self)

		# Create group box for axis selection
		axis_group = QGroupBox('Select Axes for Plotting')
		axis_layout = QVBoxLayout(axis_group)

		# Header label
		header_label = QLabel('Select exactly two axes to plot:')
		axis_layout.addWidget(header_label)

		# Create combo boxes for axis selection
		combo_layout = QHBoxLayout()

		# First axis combo
		self.x_axis_label = QLabel('X-Axis:')
		combo_layout.addWidget(self.x_axis_label)

		self.x_axis_combo = QComboBox()
		combo_layout.addWidget(self.x_axis_combo)

		# Second axis combo
		self.y_axis_label = QLabel('Y-Axis:')
		combo_layout.addWidget(self.y_axis_label)

		self.y_axis_combo = QComboBox()
		combo_layout.addWidget(self.y_axis_combo)

		axis_layout.addLayout(combo_layout)

		# Apply button
		self.apply_button = QPushButton('Apply Axis Selection')
		self.apply_button.clicked.connect(self.apply_axis_selection)
		axis_layout.addWidget(self.apply_button)

		main_layout.addWidget(axis_group)

		# Initialize with no plot manager
		self.update_axis_options()

	def set_plot_manager(self, plot_manager):
		"""Set or update the plot manager and refresh the UI"""
		self.plot_manager = plot_manager
		self.update_axis_options()

	def update_axis_options(self):
		"""Update the combo boxes with available axes from the plot manager"""
		# Clear existing items
		self.x_axis_combo.clear()
		self.y_axis_combo.clear()

		if not self.plot_manager:
			self.setEnabled(False)
			return

		self.setEnabled(True)

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
