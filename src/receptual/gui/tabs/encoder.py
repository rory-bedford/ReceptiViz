from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QGroupBox,
	QFormLayout,
	QPushButton,
	QHBoxLayout,
)
from receptual.processing.managers.data_manager import EncoderDataManager
from receptual.gui.widgets.file_selector import FileSelector
from receptual.gui.widgets.sliders import AxisSelector, RangeSelector
from receptual.processing.managers.plot_manager import PlotManager
from receptual.gui.widgets.plot_widget import Plot3DWidget


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
			plot_widget (Plot3DWidget): The main 3D plotting area.
		range_selector (QWidget): Widget for selecting plot ranges.
		axis_selector (AxisSelector): Widget for selecting axes for plotting.
		range_selector_widget (RangeSelector): Widget for selecting data ranges.
		plot_activity_btn (QPushButton): Button to display activity plots.
		plot_stimulus_btn (QPushButton): Button to display stimulus plots.
		plot_rf_btn (QPushButton): Button to display receptive field plots.
		current_plot_manager (PlotManager): Current plot manager for handling plots.
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

		self.activity_selector.reset_clicked.connect(self.on_activity_reset)
		self.stimulus_selector.reset_clicked.connect(self.on_stimulus_reset)
		self.rf_selector.reset_clicked.connect(self.on_rf_reset)

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
		# Create the 3D plot widget
		self.plot_widget = Plot3DWidget()

		# Add the plot widget to main layout
		main_layout.addWidget(
			self.plot_widget, 1
		)  # 1 = stretch factor to take available space

		# ---- RANGE SELECTOR ----
		# Range selector layout with renamed components in new order
		range_selector_layout = QVBoxLayout()

		# Create range selector widget (renamed from DataRangeSelector)
		self.range_selector_widget = RangeSelector()

		# Connect signals from range selector to update plot
		self.range_selector_widget.range_changed.connect(self.update_plot)
		self.range_selector_widget.slice_changed.connect(self.update_plot)

		# Create axis selector widget
		self.axis_selector = AxisSelector()
		self.axis_selector.axis_selected.connect(self.on_axes_selected)

		# Add to the range selector layout (range selector first, then axis selector)
		range_selector_layout.addWidget(self.range_selector_widget)
		range_selector_layout.addWidget(self.axis_selector)

		# Set range_selector_layout as the layout for range_selector
		self.range_selector = QWidget()
		self.range_selector.setLayout(range_selector_layout)

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
		# Create PlotManager with activity data
		plot_manager = PlotManager(self.data_manager.activity)
		# Update axis selector with the new plot manager
		self.axis_selector.set_plot_manager(plot_manager)
		# Update range selector with the new plot manager (renamed)
		self.range_selector_widget.set_plot_manager(plot_manager)
		# Update the 3D plot with the new plot manager
		self.plot_widget.set_plot_manager(plot_manager)
		# Store the current plot manager for later use
		self.current_plot_manager = plot_manager
		# Store which data type is currently being plotted
		self.current_plot_type = 'Activity'

	def plot_stimulus(self):
		"""Plot stimulus data"""
		# Create PlotManager with stimulus data
		plot_manager = PlotManager(self.data_manager.stimulus)
		# Update axis selector with the new plot manager
		self.axis_selector.set_plot_manager(plot_manager)
		# Update range selector with the new plot manager (renamed)
		self.range_selector_widget.set_plot_manager(plot_manager)
		# Update the 3D plot with the new plot manager
		self.plot_widget.set_plot_manager(plot_manager)
		# Store the current plot manager for later use
		self.current_plot_manager = plot_manager
		# Store which data type is currently being plotted
		self.current_plot_type = 'Stimulus'

	def plot_receptive_field(self):
		"""Plot receptive field data"""
		# Create PlotManager with receptive field data
		plot_manager = PlotManager(self.data_manager.receptive_field)
		# Update axis selector with the new plot manager
		self.axis_selector.set_plot_manager(plot_manager)
		# Update range selector with the new plot manager (renamed)
		self.range_selector_widget.set_plot_manager(plot_manager)
		# Update the 3D plot with the new plot manager
		self.plot_widget.set_plot_manager(plot_manager)
		# Store the current plot manager for later use
		self.current_plot_manager = plot_manager
		# Store which data type is currently being plotted
		self.current_plot_type = 'Receptive Field'

	def on_axes_selected(self, selected_axes):
		"""Handle axis selection from the axis selector"""
		if hasattr(self, 'current_plot_manager') and self.current_plot_manager:
			# Update the plot manager with the selected axes
			self.current_plot_manager.update_axes(selected_axes)

			# Update the range selector to show sliders for the newly selected axes (renamed)
			self.range_selector_widget.update_widgets()

			# Update the 3D plot
			self.update_plot()

	def on_activity_reset(self):
		"""Handle reset of activity data"""
		# Check if we need to clear current plot
		if hasattr(self, 'current_plot_type') and self.current_plot_type == 'Activity':
			self.clear_current_plot()

		# Continue with normal UI update
		self.update_ui_state()

	def on_stimulus_reset(self):
		"""Handle reset of stimulus data"""
		# Check if we need to clear current plot
		if hasattr(self, 'current_plot_type') and self.current_plot_type == 'Stimulus':
			self.clear_current_plot()

		# Continue with normal UI update
		self.update_ui_state()

	def on_rf_reset(self):
		"""Handle reset of receptive field data"""
		# Check if we need to clear current plot
		if (
			hasattr(self, 'current_plot_type')
			and self.current_plot_type == 'Receptive Field'
		):
			self.clear_current_plot()

		# Continue with normal UI update
		self.update_ui_state()

	def clear_current_plot(self):
		"""Clear the current plot and associated selectors"""
		# Clear the current plot manager
		if hasattr(self, 'current_plot_manager'):
			self.current_plot_manager = None

		# Reset the axis selector
		if hasattr(self, 'axis_selector'):
			self.axis_selector.set_plot_manager(None)

		# Reset the range selector
		if hasattr(self, 'range_selector_widget'):
			self.range_selector_widget.set_plot_manager(None)

		# Clear the 3D plot
		if hasattr(self, 'plot_widget'):
			self.plot_widget.set_plot_manager(None)

		# Clear the current plot type
		if hasattr(self, 'current_plot_type'):
			self.current_plot_type = None

	def update_plot(self):
		"""Update the 3D plot with current data"""
		if hasattr(self, 'plot_widget') and self.plot_widget:
			self.plot_widget.update_plot()
