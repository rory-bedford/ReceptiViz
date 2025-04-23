from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout
from receptual.processing.data_manager import EncoderDataManager
from receptual.gui.widgets.file_selector import FileSelector


class EncoderTab(QWidget):
	"""Tab for receptive field analysis"""

	def __init__(self, data_manager=None, parent=None):
		super().__init__(parent)

		# Store the data manager
		self.data_manager = (
			data_manager if data_manager is not None else EncoderDataManager()
		)

		# Initialize UI components
		self.init_ui()

	def init_ui(self):
		"""Initialize all UI components for the encoder tab"""
		# Create main layout
		main_layout = QVBoxLayout(self)

		# Create data input group
		data_group = QGroupBox('Data Input')
		data_layout = QFormLayout(data_group)

		# Create file selectors for each data type
		self.activity_selector = FileSelector(self.data_manager.activity)
		self.stimulus_selector = FileSelector(self.data_manager.stimulus)
		self.rf_selector = FileSelector(self.data_manager.receptive_field)

		# Connect signals to update UI when files are selected or reset
		self.activity_selector.file_selected.connect(self.update_ui_state)
		self.stimulus_selector.file_selected.connect(self.update_ui_state)
		self.rf_selector.file_selected.connect(self.update_ui_state)

		self.activity_selector.reset_clicked.connect(self.update_ui_state)
		self.stimulus_selector.reset_clicked.connect(self.update_ui_state)
		self.rf_selector.reset_clicked.connect(self.update_ui_state)

		# Connect data_changed signals to update all selectors
		self.activity_selector.data_changed.connect(self.update_all_selectors)
		self.stimulus_selector.data_changed.connect(self.update_all_selectors)
		self.rf_selector.data_changed.connect(self.update_all_selectors)

		# Add file selectors to layout
		data_layout.addRow(self.activity_selector)
		data_layout.addRow(self.stimulus_selector)
		data_layout.addRow(self.rf_selector)

		# Add data group to main layout
		main_layout.addWidget(data_group)

		# Add stretch to push everything to the top
		main_layout.addStretch()

	def update_ui_state(self):
		"""Update the UI state based on loaded data"""
		# Update file selector statuses
		self.activity_selector.update_status()
		self.stimulus_selector.update_status()
		self.rf_selector.update_status()

	def update_all_selectors(self):
		"""Update all selectors when one has changed"""
		self.activity_selector.update_status()
		self.stimulus_selector.update_status()
		self.rf_selector.update_status()
