from PyQt6.QtWidgets import QMenu, QMessageBox


class ResetMenu(QMenu):
	"""Menu for resetting the application state."""

	def __init__(self, parent=None, data_manager=None):
		super().__init__('Reset', parent)
		self.data_manager = data_manager
		self.parent_window = parent

		# Create action for resetting the application
		self.reset_action = self.addAction('Reset All Data')
		self.reset_action.triggered.connect(self.confirm_reset)

	def confirm_reset(self):
		"""Show confirmation dialog before resetting everything."""
		reply = QMessageBox.question(
			self.parent_window,
			'Confirm Reset',
			'This will reset all loaded and computed data. Are you sure you want to continue?',
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
			QMessageBox.StandardButton.No,
		)

		if reply == QMessageBox.StandardButton.Yes:
			self.reset_all()

	def reset_all(self):
		"""Reset the entire data manager state."""
		# Reset all components of the data manager
		if hasattr(self.data_manager, 'activity'):
			self.data_manager.activity.reset_state()

		if hasattr(self.data_manager, 'stimulus'):
			self.data_manager.stimulus.reset_state()

		if hasattr(self.data_manager, 'receptive_field'):
			self.data_manager.receptive_field.reset_state()

		# Notify the user that the reset is complete
		QMessageBox.information(
			self.parent_window,
			'Reset Complete',
			'All data has been reset successfully.',
			QMessageBox.StandardButton.Ok,
		)

		# Update the main window to reflect the reset state
		if hasattr(self.parent_window, 'update_status'):
			self.parent_window.update_status()

		# Update plot if needed
		if hasattr(self.parent_window, 'plot_widget'):
			# If plot manager exists, set it to None
			if hasattr(self.parent_window, 'plot_manager'):
				self.parent_window.plot_manager = None

			# Update UI components
			if hasattr(self.parent_window, 'axis_selector'):
				self.parent_window.axis_selector.set_plot_manager(None)

			if hasattr(self.parent_window, 'range_selector'):
				self.parent_window.range_selector.set_plot_manager(None)

			# Update the plot widget
			self.parent_window.plot_widget.set_plot_manager(None)

			# Disable sliders
			if hasattr(self.parent_window, 'sliders_container'):
				self.parent_window.sliders_container.setEnabled(False)
