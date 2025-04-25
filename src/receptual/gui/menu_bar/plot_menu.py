from PyQt6.QtWidgets import QMenu, QMessageBox


class PlotMenu(QMenu):
	"""Menu for plotting data.

	Provides options to plot Activity, Stimulus, and Receptive Field data.
	Uses the existing plot_manager for actual plotting functionality.
	"""

	def __init__(self, parent=None, data_manager=None):
		super().__init__('Plot', parent)

		self.data_manager = data_manager
		self.main_window = parent

		# Create actions for plotting different data types
		self.activity_action = self.addAction('Activity')
		self.stimulus_action = self.addAction('Stimulus')
		self.receptive_field_action = self.addAction('Receptive Field')

		# Connect signals to plot methods
		self.activity_action.triggered.connect(lambda: self.plot_data('activity'))
		self.stimulus_action.triggered.connect(lambda: self.plot_data('stimulus'))
		self.receptive_field_action.triggered.connect(
			lambda: self.plot_data('receptive_field')
		)

		# Initial update of enabled/disabled state
		self.update_action_states()

		# Connect to aboutToShow signal to update action states before menu is shown
		self.aboutToShow.connect(self.update_action_states)

	def update_action_states(self):
		"""Update enabled/disabled state of actions based on data availability."""
		# Activity is plottable if it has data (either loaded or computed)
		activity = self.data_manager.activity
		self.activity_action.setEnabled(
			(hasattr(activity, 'loaded') and activity.loaded)
			or (hasattr(activity, 'computed') and activity.computed)
		)

		# Stimulus is plottable if it has data (either loaded or computed)
		stimulus = self.data_manager.stimulus
		self.stimulus_action.setEnabled(
			(hasattr(stimulus, 'loaded') and stimulus.loaded)
			or (hasattr(stimulus, 'computed') and stimulus.computed)
		)

		# Receptive field is plottable if it has data (either loaded or computed)
		rf = self.data_manager.receptive_field
		self.receptive_field_action.setEnabled(
			(hasattr(rf, 'loaded') and rf.loaded)
			or (hasattr(rf, 'computed') and rf.computed)
		)

	def plot_data(self, plot_type):
		"""Create and display plot for the specified data type.

		Args:
			plot_type: Type of plot to generate ("activity", "stimulus", or "receptive_field")
		"""
		try:
			# Check data is available
			if plot_type == 'activity' and not (
				self.data_manager.activity.loaded or self.data_manager.activity.computed
			):
				raise ValueError('Activity data not available')

			elif plot_type == 'stimulus' and not (
				self.data_manager.stimulus.loaded or self.data_manager.stimulus.computed
			):
				raise ValueError('Stimulus data not available')

			elif plot_type == 'receptive_field' and not (
				self.data_manager.receptive_field.loaded
				or self.data_manager.receptive_field.computed
			):
				raise ValueError('Receptive Field data not available')

			# Tell the main window to set up the plot manager with the correct data type
			if hasattr(self.main_window, 'set_plot_manager'):
				self.main_window.set_plot_manager(plot_type)
			else:
				raise AttributeError('Main window has no set_plot_manager method')

		except Exception as e:
			QMessageBox.critical(
				self.parent(),
				'Error',
				f'Failed to plot {plot_type}: {str(e)}',
				QMessageBox.StandardButton.Ok,
			)
