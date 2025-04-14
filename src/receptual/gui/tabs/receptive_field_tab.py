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
from receptual.processing.receptive_field import ReceptiveFieldProcessor


class ReceptiveFieldTab(QWidget):
	"""Tab for receptive field analysis"""

	def __init__(self, parent=None):
		super().__init__(parent)

		# Create the processor (shared between widgets)
		self.processor = ReceptiveFieldProcessor()
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

		# Connect validation signals to update button state
		self.activity_selector.validation_changed.connect(self.update_button_state)
		self.stimulus_selector.validation_changed.connect(self.update_button_state)

		# Dimension editing button - taller to fill the height of both selectors
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
		top_layout.addWidget(self.dimension_button, 0, 1, 2, 1)  # Span 2 rows

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

		# Enable individual plot buttons based on file validity
		self.plot_stimulus_button.setEnabled(stimulus_valid)
		self.plot_activity_button.setEnabled(activity_valid)
		self.plot_rf_button.setEnabled(activity_valid and stimulus_valid)
		self.dimension_button.setEnabled(activity_valid or stimulus_valid)

	def show_dimension_editor(self):
		"""Show unified dimension editor dialog"""
		# Only show if at least one file is valid
		if (
			not self.activity_selector.is_valid_file()
			and not self.stimulus_selector.is_valid_file()
		):
			return

		editor_dialog = DimensionEditorDialog(self.processor, self)
		if editor_dialog.exec():
			# Update dimension info display in both selectors
			self.activity_selector.update_dimension_info()
			self.stimulus_selector.update_dimension_info()

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
