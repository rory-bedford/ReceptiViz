import os
from PyQt6.QtWidgets import QMenu, QFileDialog, QMessageBox


class SaveMenu(QMenu):
	"""Menu for saving data files.

	Provides options to save Activity, Stimulus, and Receptive Field data.
	"""

	# Class variable to store the last visited directory
	last_directory = os.getcwd()

	def __init__(self, parent=None, data_manager=None):
		super().__init__('Save', parent)

		self.data_manager = data_manager

		# Create actions for saving different data types
		self.activity_action = self.addAction('Activity')
		self.stimulus_action = self.addAction('Stimulus')
		self.receptive_field_action = self.addAction('Receptive Field')

		# Connect signals to save method with appropriate data manager component
		self.activity_action.triggered.connect(
			lambda: self.save_data(self.data_manager.activity)
		)
		self.stimulus_action.triggered.connect(
			lambda: self.save_data(self.data_manager.stimulus)
		)
		self.receptive_field_action.triggered.connect(
			lambda: self.save_data(self.data_manager.receptive_field)
		)

		# Initial update of enabled/disabled state
		self.update_action_states()

		# Connect to aboutToShow signal to update action states before menu is shown
		self.aboutToShow.connect(self.update_action_states)

	def update_action_states(self):
		"""Update enabled/disabled state of actions based on component computed status."""
		self.activity_action.setEnabled(
			hasattr(self.data_manager.activity, 'computed')
			and self.data_manager.activity.computed
		)
		self.stimulus_action.setEnabled(
			hasattr(self.data_manager.stimulus, 'computed')
			and self.data_manager.stimulus.computed
		)
		self.receptive_field_action.setEnabled(
			hasattr(self.data_manager.receptive_field, 'computed')
			and self.data_manager.receptive_field.computed
		)

	def save_data(self, data_component):
		"""Generic method to save a data component to a .npy file.

		Args:
			data_component: The data component (activity, stimulus, receptive_field)
							to save.
		"""
		component_name = data_component.name

		file_path, _ = QFileDialog.getSaveFileName(
			self.parent(),
			f'Save {component_name} Data',
			os.path.join(SaveMenu.last_directory, f'{component_name.lower()}.npy'),
			'NumPy Files (*.npy)',
		)

		if file_path:
			# Update the last directory used
			SaveMenu.last_directory = os.path.dirname(file_path)

			# Add .npy extension if not present
			if not file_path.lower().endswith('.npy'):
				file_path += '.npy'

			try:
				# Call the save_data method from the data component
				success = data_component.save_data(file_path)

				if success:
					# Show success message
					QMessageBox.information(
						self.parent(),
						'Success',
						f'{component_name} data saved successfully to {file_path}',
						QMessageBox.StandardButton.Ok,
					)
				else:
					# Show error message
					QMessageBox.critical(
						self.parent(),
						'Error',
						f'Failed to save {component_name.lower()} data.',
						QMessageBox.StandardButton.Ok,
					)
			except Exception as e:
				# Handle any unexpected exceptions
				QMessageBox.critical(
					self.parent(),
					'Error',
					f'Unexpected error saving {component_name.lower()}: {str(e)}',
					QMessageBox.StandardButton.Ok,
				)
