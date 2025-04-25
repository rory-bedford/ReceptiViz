import os
from PyQt6.QtWidgets import QMenu, QFileDialog, QMessageBox


class LoadMenu(QMenu):
	"""Menu for loading data files.

	Provides options to load Activity, Stimulus, and Receptive Field data.
	"""

	# Class variable to store the last visited directory
	last_directory = os.getcwd()

	def __init__(self, parent=None, data_manager=None):
		super().__init__('Load', parent)

		self.data_manager = data_manager

		# Create actions for loading different data types
		self.activity_action = self.addAction('Activity')
		self.stimulus_action = self.addAction('Stimulus')
		self.receptive_field_action = self.addAction('Receptive Field')

		# Connect signals to load method with appropriate data manager component
		self.activity_action.triggered.connect(
			lambda: self.load_data(self.data_manager.activity)
		)
		self.stimulus_action.triggered.connect(
			lambda: self.load_data(self.data_manager.stimulus)
		)
		self.receptive_field_action.triggered.connect(
			lambda: self.load_data(self.data_manager.receptive_field)
		)

		# Initial update of enabled/disabled state
		self.update_action_states()

		# Connect to aboutToShow signal to update action states before menu is shown
		self.aboutToShow.connect(self.update_action_states)

	def update_action_states(self):
		"""Update enabled/disabled state of actions based on component availability."""
		self.activity_action.setEnabled(self.data_manager.activity.available)
		self.stimulus_action.setEnabled(self.data_manager.stimulus.available)
		self.receptive_field_action.setEnabled(
			self.data_manager.receptive_field.available
		)

	def load_data(self, data_component):
		"""Generic method to load data from a .npy file into a data component.

		Args:
			data_component: The data component (activity, stimulus, receptive_field)
							to load data into.
		"""
		component_name = data_component.name

		file_path, _ = QFileDialog.getOpenFileName(
			self.parent(),
			f'Load {component_name} Data',
			LoadMenu.last_directory,  # Use the last directory instead of home
			'NumPy Files (*.npy)',
		)

		if file_path:
			# Update the last directory used
			LoadMenu.last_directory = os.path.dirname(file_path)

			# Call the set_data method from the data component
			success = data_component.set_data(file_path)

			if success:
				# Show success message
				QMessageBox.information(
					self.parent(),
					'Success',
					f'{component_name} data loaded successfully.',
					QMessageBox.StandardButton.Ok,
				)
			else:
				# Show error message with details
				error_message = f'Error loading {component_name.lower()} data:\n'
				if data_component.errors:
					error_message += '\n'.join(data_component.errors)
				else:
					error_message += 'Unknown error occurred.'

				QMessageBox.critical(
					self.parent(), 'Error', error_message, QMessageBox.StandardButton.Ok
				)

			# Update action states after loading
			self.update_action_states()
