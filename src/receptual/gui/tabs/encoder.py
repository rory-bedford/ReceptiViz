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
		self.processor = EncoderDataManager()
		self.processor.set_sample_rate(10.0)  # Default sample rate to 10Hz
		self.plot_widget = None

		# Set up main layout
		main_layout = QVBoxLayout(self)

		# Create UI components
		main_layout.addWidget(self._create_file_selection_section())

		# Plot widget container
		self.plot_container = QWidget()
		self.plot_layout = QVBoxLayout(self.plot_container)
		main_layout.addWidget(
			self.plot_container, 1
		)  # Give plot container stretch priority

		# Add plot buttons
		main_layout.addWidget(
			self._create_button_section(), 0, Qt.AlignmentFlag.AlignCenter
		)

	def _create_file_selection_section(self):
		"""Create the file selection and dimension editor section"""
		section = QWidget()
		layout = QGridLayout(section)
		layout.setColumnStretch(0, 6)  # File selectors get much more space
		layout.setColumnStretch(1, 1)  # Dimension editor gets minimal space

		# Create file selection widgets with connection to specific data set methods
		self.activity_selector = FileSelectionWidget(
			'Activity Array:', 'activity', self.processor
		)
		self.stimulus_selector = FileSelectionWidget(
			'Stimulus Array:', 'stimulus', self.processor
		)
		self.receptive_field_selector = FileSelectionWidget(
			'Receptive Field Array:', 'receptive_field', self.processor
		)

		# Connect file selection signals to the appropriate data manager methods
		self.activity_selector.file_selected.connect(self._on_activity_file_selected)
		self.stimulus_selector.file_selected.connect(self._on_stimulus_file_selected)
		self.receptive_field_selector.file_selected.connect(self._on_rf_file_selected)

		# Dimension editing button
		self.dimension_button = QPushButton('Edit\nDimensions')
		self.dimension_button.setEnabled(False)
		self.dimension_button.clicked.connect(self.show_dimension_editor)
		self.dimension_button.setSizePolicy(
			QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
		)
		self.dimension_button.setMaximumWidth(100)

		# Add widgets to the layout
		layout.addWidget(self.activity_selector, 0, 0)
		layout.addWidget(self.stimulus_selector, 1, 0)
		layout.addWidget(self.receptive_field_selector, 2, 0)
		layout.addWidget(self.dimension_button, 0, 1, 3, 1)  # Span 3 rows

		return section

	def _create_button_section(self):
		"""Create the plot buttons section"""
		container = QWidget()
		layout = QHBoxLayout(container)

		# Create plot buttons
		self.plot_stimulus_button = QPushButton('Plot Stimulus')
		self.plot_activity_button = QPushButton('Plot Activity')
		self.plot_rf_button = QPushButton('Plot Receptive Field')

		# Configure buttons
		buttons = [
			self.plot_stimulus_button,
			self.plot_activity_button,
			self.plot_rf_button,
		]
		for button in buttons:
			button.setMinimumWidth(150)
			button.setMinimumHeight(40)
			button.setEnabled(False)

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

		# Add buttons to layout with stretches for centering
		layout.addStretch()
		for button in buttons:
			layout.addWidget(button)
		layout.addStretch()

		return container

	def _on_activity_file_selected(self, file_path):
		"""Handle activity file selection using the data manager's set_activity method"""
		self.processor.clear_errors()
		success = self.processor.set_activity(file_path)

		if not success:
			self.show_error(
				'Activity Array Error', '\n'.join(self.processor.get_errors())
			)

		# Update UI state regardless of success
		self.update_selector_visibilities()
		self.update_button_state()
		self.activity_selector.update_dimension_info()
		self.receptive_field_selector.update_dimension_info()  # RF might have changed

	def _on_stimulus_file_selected(self, file_path):
		"""Handle stimulus file selection using the data manager's set_stimulus method"""
		self.processor.clear_errors()
		success = self.processor.set_stimulus(file_path)

		if not success:
			self.show_error(
				'Stimulus Array Error', '\n'.join(self.processor.get_errors())
			)

		# Update UI state regardless of success
		self.update_button_state()
		self.stimulus_selector.update_dimension_info()

	def _on_rf_file_selected(self, file_path):
		"""Handle receptive field file selection using the data manager's set_receptive_field method"""
		self.processor.clear_errors()
		success = self.processor.set_receptive_field(file_path)

		if not success:
			self.show_error(
				'Receptive Field Array Error', '\n'.join(self.processor.get_errors())
			)

		# Update UI state regardless of success
		self.update_selector_visibilities()
		self.update_button_state()
		self.receptive_field_selector.update_dimension_info()
		self.activity_selector.update_dimension_info()  # Activity might have changed

	def update_selector_visibilities(self):
		"""Update which selectors are enabled based on loaded data"""
		# Check what data we have
		has_activity = self.processor.activity is not None
		has_rf = self.processor.receptive_field is not None

		# If we have activity data, disable the RF selector (incompatible)
		if has_activity:
			self.activity_selector.setEnabled(True)
			self.receptive_field_selector.setEnabled(False)
		# If we have RF data, disable the activity selector (incompatible)
		elif has_rf:
			self.activity_selector.setEnabled(False)
			self.receptive_field_selector.setEnabled(True)
		# If we have neither, enable both as options
		else:
			self.activity_selector.setEnabled(True)
			self.receptive_field_selector.setEnabled(True)

		# Stimulus selector is always enabled
		self.stimulus_selector.setEnabled(True)

	def update_button_state(self):
		"""Update the state of plot buttons based on available data"""
		# Check what data we have
		has_activity = self.processor.activity is not None
		has_stimulus = self.processor.stimulus is not None
		has_rf = self.processor.receptive_field is not None

		# Enable buttons based on available data
		self.plot_stimulus_button.setEnabled(has_stimulus)
		self.plot_activity_button.setEnabled(has_activity)

		# RF can be plotted if:
		# 1. We have a loaded RF file, or
		# 2. We have both activity and stimulus which can be used to calculate RF
		can_plot_rf = has_rf or (has_activity and has_stimulus)
		self.plot_rf_button.setEnabled(can_plot_rf)

		# Enable dimension editor if any data is available
		self.dimension_button.setEnabled(has_activity or has_stimulus or has_rf)

	def show_dimension_editor(self):
		"""Show unified dimension editor dialog"""
		if not (
			self.processor.activity is not None
			or self.processor.stimulus is not None
			or self.processor.receptive_field is not None
		):
			return

		editor_dialog = DimensionEditorDialog(self.processor, self)
		if editor_dialog.exec():
			# Update dimension info display in all selectors
			for selector in [
				self.activity_selector,
				self.stimulus_selector,
				self.receptive_field_selector,
			]:
				selector.update_dimension_info()

	def generate_plot(self, plot_type):
		"""Generate the specified type of plot"""
		self.processor.clear_errors()
		try:
			if (
				plot_type == 'receptive_field'
				and self.processor.receptive_field is None
			):
				# Need to calculate RF on the fly
				if not self.processor.activity or not self.processor.stimulus:
					self.show_error(
						'Error',
						'Both activity and stimulus are required to calculate receptive field',
					)
					return

				# The data manager's validate_compatibility method will check compatibility
				# between activity and stimulus for RF calculation
				self.processor.validate_compatibility()

				if self.processor.get_errors():
					self.show_error(
						'Validation Error', '\n'.join(self.processor.get_errors())
					)
					return

				# Process data to generate the receptive field
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
		QMessageBox.critical(self, title, message)
