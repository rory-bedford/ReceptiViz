from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QGroupBox,
	QFormLayout,
	QPushButton,
	QHBoxLayout,
	QFrame,
)
from receptual.processing.data_manager import EncoderDataManager
from receptual.gui.widgets.file_selector import FileSelector


class EncoderTab(QWidget):
	"""Tab for receptive field analysis

	This tab provides interfaces for loading neurophysiological data,
	visualizing it, selecting ranges to analyze, and switching between
	different data types for plotting.

	Attributes:
		data_manager (EncoderDataManager): Manager for handling data.
		activity_selector (FileSelector): Widget for selecting activity data.
		stimulus_selector (FileSelector): Widget for selecting stimulus data.
		rf_selector (FileSelector): Widget for selecting receptive field data.
		plot_frame (QFrame): The main plotting area.
		range_selector (QFrame): Widget for selecting plot ranges (placeholder).
		plot_activity_btn (QPushButton): Button to display activity plots.
		plot_stimulus_btn (QPushButton): Button to display stimulus plots.
		plot_rf_btn (QPushButton): Button to display receptive field plots.
	"""

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
		main_layout.setContentsMargins(5, 5, 5, 5)
		main_layout.setSpacing(5)

		# ---- TOP SECTION: DATA INPUT ----
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

		# Connect compute_clicked signals to update UI
		self.activity_selector.compute_clicked.connect(self.update_ui_state)
		self.stimulus_selector.compute_clicked.connect(self.update_ui_state)
		self.rf_selector.compute_clicked.connect(self.update_ui_state)

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

		# ---- MIDDLE SECTION: PLOT AREA ----
		# Create a frame to hold the plot (we'll replace this with actual plot later)
		self.plot_frame = QFrame()
		self.plot_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
		self.plot_frame.setMinimumHeight(400)  # Set a minimum height
		self.plot_frame.setStyleSheet(
			'background-color: #f0f0f0;'
		)  # Light gray background

		# Add plot frame to main layout
		main_layout.addWidget(
			self.plot_frame, 1
		)  # 1 = stretch factor to take available space

		# ---- RANGE SELECTOR ----
		# Placeholder for range selector widget
		self.range_selector = QFrame()
		self.range_selector.setFrameStyle(
			QFrame.Shape.StyledPanel | QFrame.Shadow.Raised
		)
		self.range_selector.setMinimumHeight(80)
		self.range_selector.setStyleSheet(
			'background-color: #e0e0e0;'
		)  # Slightly darker gray

		# Add range selector to main layout
		main_layout.addWidget(self.range_selector)

		# ---- BOTTOM SECTION: PLOT BUTTONS ----
		# Create a horizontal layout for the plot buttons
		button_layout = QHBoxLayout()

		# Create plot buttons
		self.plot_activity_btn = QPushButton('Plot Activity')
		self.plot_stimulus_btn = QPushButton('Plot Stimulus')
		self.plot_rf_btn = QPushButton('Plot Receptive Field')

		# Connect plot buttons to their respective actions
		self.plot_activity_btn.clicked.connect(self.plot_activity)
		self.plot_stimulus_btn.clicked.connect(self.plot_stimulus)
		self.plot_rf_btn.clicked.connect(self.plot_receptive_field)

		# Add buttons to layout
		button_layout.addWidget(self.plot_activity_btn)
		button_layout.addWidget(self.plot_stimulus_btn)
		button_layout.addWidget(self.plot_rf_btn)

		# Add button layout to main layout
		main_layout.addLayout(button_layout)

		# Initialize the UI state
		self.update_ui_state()

	def update_ui_state(self):
		"""Update the UI state based on loaded data"""
		# Update file selector statuses
		self.activity_selector.update_status()
		self.stimulus_selector.update_status()
		self.rf_selector.update_status()

		# Update plot button availability based on whether data is loaded OR computed
		self.plot_activity_btn.setEnabled(
			(
				hasattr(self.data_manager.activity, 'loaded')
				and self.data_manager.activity.loaded
			)
			or (
				hasattr(self.data_manager.activity, 'computed')
				and self.data_manager.activity.computed
			)
		)
		self.plot_stimulus_btn.setEnabled(
			(
				hasattr(self.data_manager.stimulus, 'loaded')
				and self.data_manager.stimulus.loaded
			)
			or (
				hasattr(self.data_manager.stimulus, 'computed')
				and self.data_manager.stimulus.computed
			)
		)
		self.plot_rf_btn.setEnabled(
			(
				hasattr(self.data_manager.receptive_field, 'loaded')
				and self.data_manager.receptive_field.loaded
			)
			or (
				hasattr(self.data_manager.receptive_field, 'computed')
				and self.data_manager.receptive_field.computed
			)
		)

	def update_all_selectors(self):
		"""Update all selectors when one has changed"""
		self.activity_selector.update_status()
		self.stimulus_selector.update_status()
		self.rf_selector.update_status()

	def plot_activity(self):
		"""Plot activity data"""
		pass

	def plot_stimulus(self):
		"""Plot stimulus data"""
		pass

	def plot_receptive_field(self):
		"""Plot receptive field data"""
		pass
