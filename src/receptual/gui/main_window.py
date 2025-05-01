from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QFrame
from PyQt6.QtCore import pyqtSlot

from receptual.processing.managers.data_manager import DataManager
from receptual.gui.menu_bar.menu_bar import MenuBar
from receptual.gui.widgets.status import StatusWidget
from receptual.gui.widgets.sliders import AxisSelector, RangeSelector
from receptual.gui.widgets.plot_widget import Plot3DWidget


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle('Receptual')

		# Create central widget
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)

		# Create layout
		self.layout = QVBoxLayout(self.central_widget)
		self.layout.setContentsMargins(10, 10, 10, 10)
		self.layout.setSpacing(8)

		# Initialize data manager and plot manager
		self.data_manager = DataManager()
		self.plot_manager = None

		# Create and set the menu bar
		self.menu_bar = MenuBar(self, self.data_manager)
		self.setMenuBar(self.menu_bar)

		# Create status widget at top
		self.status_widget = StatusWidget(self, self.data_manager)
		self.layout.addWidget(self.status_widget)

		# Create a frame to contain the plot widget with a border
		plot_frame = QFrame()
		plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
		plot_frame.setMinimumHeight(300)
		plot_layout = QVBoxLayout(plot_frame)
		plot_layout.setContentsMargins(0, 0, 0, 0)

		# Create the 3D plot widget and add it to the frame
		self.plot_widget = Plot3DWidget(self.plot_manager)
		plot_layout.addWidget(self.plot_widget)

		# Add the frame to the main layout with stretch priority
		self.layout.addWidget(plot_frame, 1)

		# Create slider widgets container at bottom
		self.sliders_container = QWidget()
		sliders_layout = QVBoxLayout(self.sliders_container)
		sliders_layout.setContentsMargins(0, 0, 0, 0)
		sliders_layout.setSpacing(5)

		# Add RangeSelector
		self.range_selector = RangeSelector(self.plot_manager)
		sliders_layout.addWidget(self.range_selector)

		# Add AxisSelector
		self.axis_selector = AxisSelector(self.plot_manager)
		sliders_layout.addWidget(self.axis_selector)

		# Add the sliders container to main layout
		self.layout.addWidget(self.sliders_container)

		# Initially disable the slider widgets until plot_manager is set
		self.sliders_container.setEnabled(False)

		# Set size
		self.resize(800, 600)

		# Connect update triggers
		self.connect_update_triggers()

		# Connect range and axis selectors to update the plot
		self.range_selector.range_changed.connect(self.update_plot)
		self.range_selector.slice_changed.connect(self.update_plot)
		self.axis_selector.axis_selected.connect(self.update_plot)

		# Connect axis selector to range selector to ensure coordination
		self.axis_selector.axis_selected.connect(self.update_range_selector)

	def connect_update_triggers(self):
		"""Connect events that should trigger a status update."""
		# Update status after menu operations
		# Note: We're now checking if attributes exist before accessing them

		# Check if load_menu exists (it won't until implemented)
		if hasattr(self.menu_bar, 'load_menu'):
			for action in self.menu_bar.load_menu.actions():
				action.triggered.connect(self.update_status)

		# Check if compute_menu exists (it won't until implemented)
		if hasattr(self.menu_bar, 'compute_menu'):
			for action in self.menu_bar.compute_menu.actions():
				action.triggered.connect(self.update_status)

		# Initial status update
		self.update_status()

	def update_status(self):
		"""Update the status widget."""
		self.status_widget.update_status()

	@pyqtSlot(str)
	def set_plot_manager(self, plot_type):
		"""Set the plot manager based on the data type.

		Args:
			plot_type: String indicating the type of data to plot ('activity', 'stimulus', or 'receptive_field')
		"""
		# Import plot_manager module dynamically to avoid circular imports
		from receptual.processing.managers.plot_manager import PlotManager

		try:
			# Create appropriate plot manager based on data type
			if plot_type == 'activity':
				if (
					not self.data_manager.activity.loaded
					and not self.data_manager.activity.computed
				):
					raise ValueError('Activity data is not available')
				data_component = self.data_manager.activity

			elif plot_type == 'stimulus':
				if (
					not self.data_manager.stimulus.loaded
					and not self.data_manager.stimulus.computed
				):
					raise ValueError('Stimulus data is not available')
				data_component = self.data_manager.stimulus

			elif plot_type == 'receptive_field':
				if (
					not self.data_manager.receptive_field.loaded
					and not self.data_manager.receptive_field.computed
				):
					raise ValueError('Receptive Field data is not available')
				data_component = self.data_manager.receptive_field
			else:
				raise ValueError(f'Unknown plot type: {plot_type}')

			# Create plot manager with the data component
			self.plot_manager = PlotManager(data_component)

			# First update the sliders with the new plot manager
			self.axis_selector.set_plot_manager(self.plot_manager)
			self.range_selector.set_plot_manager(self.plot_manager)

			# After sliders are ready, update the plot widget
			self.plot_widget.set_plot_manager(self.plot_manager)

			# Enable the sliders container
			self.sliders_container.setEnabled(True)

			# Make sure the plot is created by explicitly calling update_plot
			self.update_plot()

		except Exception as e:
			from PyQt6.QtWidgets import QMessageBox

			QMessageBox.critical(
				self,
				'Plot Error',
				f'Error setting up plot: {str(e)}',
				QMessageBox.StandardButton.Ok,
			)

	def update_plot(self):
		"""Update the current plot."""
		if self.plot_manager:
			try:
				# First ensure the plot_manager has the latest data
				self.plot_widget.set_plot_manager(self.plot_manager)

				# Then update the plot
				self.plot_widget.update_plot()

			except Exception as e:
				from PyQt6.QtWidgets import QMessageBox

				QMessageBox.warning(
					self,
					'Plot Warning',
					f'Error updating plot: {str(e)}',
					QMessageBox.StandardButton.Ok,
				)

	def update_range_selector(self):
		"""Update the range selector when axes selection changes"""
		if self.plot_manager:
			self.range_selector.update_widgets()
