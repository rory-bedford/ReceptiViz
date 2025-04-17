from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QPushButton,
	QMessageBox,
	QHBoxLayout,
	QGridLayout,
	QSizePolicy,
)
from PyQt6.QtCore import Qt
from receptual.gui.widgets.file_selection import FileSelectionWidget
from receptual.gui.widgets.plot_widget import PlotWidget
from receptual.gui.widgets.dimension_editor import DimensionEditorDialog
from receptual.processing.data_manager import EncoderDataManager


class EncoderTab(QWidget):
	"""Tab for receptive field analysis"""

	def __init__(self, parent=None):
		super().__init__(parent)

		# Create the processor (shared between widgets)
		self.processor = EncoderDataManager()
		self.processor.set_sample_rate(10.0)  # Default sample rate to 10Hz

		# Set up main layout
		main_layout = QVBoxLayout(self)

		# File selectors and options section
		top_section_widget = QWidget()
		top_layout = QGridLayout(top_section_widget)
		top_layout.setColumnStretch(0, 6)  # File selectors get much more space
		top_layout.setColumnStretch(1, 1)  # Dimension editor gets minimal space

		# Create file selection widgets that use the processor for validation
		self.activity_selector = FileSelectionWidget(
			'Activity Array:', 'activity', self.processor
		)
		self.stimulus_selector = FileSelectionWidget(
			'Stimulus Array:', 'stimulus', self.processor
		)
		self.receptive_field_selector = FileSelectionWidget(
			'Receptive Field Array:', 'receptive_field', self.processor
		)

		# Connect validation signals to update button state
		self.activity_selector.validation_changed.connect(self.update_button_state)
		self.stimulus_selector.validation_changed.connect(self.update_button_state)
		self.receptive_field_selector.validation_changed.connect(
			self.update_button_state
		)

		# Also connect file selection changes
		self.activity_selector.file_selected.connect(self.update_button_state)
		self.stimulus_selector.file_selected.connect(self.update_button_state)
		self.receptive_field_selector.file_selected.connect(self.update_button_state)

		# Dimension editing button - taller to fill the height of all selectors
		self.dimension_button = QPushButton('Edit\nDimensions')
		self.dimension_button.setEnabled(False)
		self.dimension_button.clicked.connect(self.show_dimension_editor)
		self.dimension_button.setSizePolicy(
			QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
		)
		self.dimension_button.setMaximumWidth(100)  # Restrict width

		# Add widgets to the top layout
		top_layout.addWidget(self.activity_selector, 0, 0)
		top_layout.addWidget(self.stimulus_selector, 1, 0)
		top_layout.addWidget(self.receptive_field_selector, 2, 0)
		top_layout.addWidget(self.dimension_button, 0, 1, 3, 1)  # Span 3 rows

		# Add top section to main layout
		main_layout.addWidget(top_section_widget)

		# Plot widget container (initially empty)
		self.plot_container = QWidget()
		self.plot_layout = QVBoxLayout(self.plot_container)
		self.plot_widget = None

		# Add widgets to main layout
		main_layout.addWidget(
			self.plot_container, 1
		)  # Give plot container the stretch priority

		# Create button container for the three plot buttons
		button_container = QWidget()
		button_layout = QHBoxLayout(button_container)

		# Create the three plot buttons
		self.plot_stimulus_button = QPushButton('Plot Stimulus')
		self.plot_activity_button = QPushButton('Plot Activity')
		self.plot_rf_button = QPushButton('Plot Receptive Field')

		# Set minimum sizes for buttons
		for button in [
			self.plot_stimulus_button,
			self.plot_activity_button,
			self.plot_rf_button,
		]:
			button.setMinimumWidth(150)
			button.setMinimumHeight(40)
			button.setEnabled(False)

		# Add buttons to layout
		button_layout.addStretch()  # Add stretch before buttons
		button_layout.addWidget(self.plot_stimulus_button)
		button_layout.addWidget(self.plot_activity_button)
		button_layout.addWidget(self.plot_rf_button)
		button_layout.addStretch()  # Add stretch after buttons

		# Connect button signals
		self.plot_stimulus_button.clicked.connect(
			lambda: self.generate_plot('stimulus')
		)
		self.plot_activity_button.clicked.connect(
			lambda: self.generate_plot('activity')
		)
		self.plot_rf_button.clicked.connect(
			lambda: self.generate_plot('receptive_field')
		)

		# Add the button container to main layout
		main_layout.addWidget(button_container, 0, Qt.AlignmentFlag.AlignCenter)

	def update_button_state(self, _=None):
		"""Update the state of the buttons based on file validity"""
		activity_valid = self.activity_selector.is_valid_file()
		stimulus_valid = self.stimulus_selector.is_valid_file()
		receptive_field_valid = self.receptive_field_selector.is_valid_file()

		# Define the two valid modes and check current state
		activity_mode = activity_valid
		direct_rf_mode = receptive_field_valid

		# If both are active, prioritize the most recently selected one
		if activity_valid and receptive_field_valid:
			# This shouldn't happen with our UI logic, but handle it just in case
			self.set_selector_enabled(self.receptive_field_selector, False)
			self.set_selector_enabled(self.activity_selector, True)
			direct_rf_mode = False
		else:
			# Otherwise enable/disable based on the current mode
			if activity_mode:
				# In activity mode, disable RF selector
				self.set_selector_enabled(self.activity_selector, True)
				self.set_selector_enabled(self.receptive_field_selector, False)
			elif direct_rf_mode:
				# In RF mode, disable activity selector
				self.set_selector_enabled(self.receptive_field_selector, True)
				self.set_selector_enabled(self.activity_selector, False)
			else:
				# If no selection yet, enable both options
				self.set_selector_enabled(self.receptive_field_selector, True)
				self.set_selector_enabled(self.activity_selector, True)

		# Stimulus is always enabled
		self.set_selector_enabled(self.stimulus_selector, True)

		# Enable individual plot buttons based on file validity
		self.plot_stimulus_button.setEnabled(stimulus_valid)
		self.plot_activity_button.setEnabled(activity_valid)

		# Receptive field can be plotted if:
		# 1. Direct RF mode with valid RF file
		# 2. Activity mode with valid activity and stimulus files
		rf_plot_enabled = (direct_rf_mode and receptive_field_valid) or (
			activity_mode and activity_valid and stimulus_valid
		)
		self.plot_rf_button.setEnabled(rf_plot_enabled)

		# Enable dimension editor if any file is valid
		self.dimension_button.setEnabled(
			activity_valid or stimulus_valid or receptive_field_valid
		)

	def set_selector_enabled(self, selector, enabled):
		"""Enable or disable a file selector while keeping it visible"""
		selector.setEnabled(enabled)
		# Keep the file info visible but gray out the controls
		for child in selector.findChildren(QPushButton) + selector.findChildren(
			QWidget
		):
			if hasattr(child, 'setEnabled'):
				child.setEnabled(enabled)

	def show_dimension_editor(self):
		"""Show unified dimension editor dialog"""
		# Only show if at least one file is valid
		if (
			not self.activity_selector.is_valid_file()
			and not self.stimulus_selector.is_valid_file()
			and not self.receptive_field_selector.is_valid_file()
		):
			return

		editor_dialog = DimensionEditorDialog(self.processor, self)
		if editor_dialog.exec():
			# Update dimension info display in all selectors
			self.activity_selector.update_dimension_info()
			self.stimulus_selector.update_dimension_info()
			self.receptive_field_selector.update_dimension_info()

	def generate_plot(self, plot_type):
		"""Generate the specified type of plot"""
		try:
			if plot_type == 'receptive_field':
				# Validate compatibility between arrays
				self.processor.validate_compatibility()

				if self.processor.get_errors():
					self.show_error(
						'Validation Error', '\n'.join(self.processor.get_errors())
					)
					return

				# Process the data
				self.processor.process()

				if self.processor.get_errors():
					self.show_error(
						'Processing Error', '\n'.join(self.processor.get_errors())
					)
					return

			# Update the plot
			if self.plot_widget:
				self.plot_layout.removeWidget(self.plot_widget)
				self.plot_widget.deleteLater()

			self.plot_widget = PlotWidget(self.processor, plot_type)
			self.plot_layout.addWidget(self.plot_widget)

		except Exception as e:
			self.show_error('Error', str(e))

	def show_error(self, title, message):
		"""Show an error message"""
		msg_box = QMessageBox(self)
		msg_box.setIcon(QMessageBox.Icon.Critical)
		msg_box.setWindowTitle(title)
		msg_box.setText(message)
		msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
		msg_box.exec()
