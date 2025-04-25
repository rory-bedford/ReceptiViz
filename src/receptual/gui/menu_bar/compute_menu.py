from PyQt6.QtWidgets import QMenu, QMessageBox


class ComputeMenu(QMenu):
	"""Menu for computing data.

	Provides options to compute Activity, Stimulus, and Receptive Field.
	"""

	def __init__(self, parent=None, data_manager=None):
		super().__init__('Compute', parent)

		self.data_manager = data_manager

		# Create actions for computing different data types
		self.activity_action = self.addAction('Activity')
		self.stimulus_action = self.addAction('Stimulus')
		self.receptive_field_action = self.addAction('Receptive Field')

		# Connect signals to compute methods
		self.activity_action.triggered.connect(
			lambda: self.compute_data(self.data_manager.activity)
		)
		self.stimulus_action.triggered.connect(
			lambda: self.compute_data(self.data_manager.stimulus)
		)
		self.receptive_field_action.triggered.connect(
			lambda: self.compute_data(self.data_manager.receptive_field)
		)

		# Initial update of enabled/disabled state
		self.update_action_states()

		# Connect to aboutToShow signal to update action states before menu is shown
		self.aboutToShow.connect(self.update_action_states)

	def update_action_states(self):
		"""Update enabled/disabled state of actions based on component computability."""
		self.activity_action.setEnabled(
			hasattr(self.data_manager.activity, 'computable')
			and self.data_manager.activity.computable
		)
		self.stimulus_action.setEnabled(
			hasattr(self.data_manager.stimulus, 'computable')
			and self.data_manager.stimulus.computable
		)
		self.receptive_field_action.setEnabled(
			hasattr(self.data_manager.receptive_field, 'computable')
			and self.data_manager.receptive_field.computable
		)

	def compute_data(self, data_component):
		"""Generic method to compute a data component.

		Args:
			data_component: The data component (activity, stimulus, receptive_field) to compute.
		"""
		component_name = data_component.name

		try:
			success = data_component.compute()

			if success:
				# Show success message
				QMessageBox.information(
					self.parent(),
					'Success',
					f'{component_name} computed successfully.',
					QMessageBox.StandardButton.Ok,
				)
			else:
				# Show error message with details
				error_message = f'Error computing {component_name.lower()}:\n'
				if hasattr(data_component, 'errors') and data_component.errors:
					error_message += '\n'.join(data_component.errors)
				else:
					error_message += 'Unknown error occurred.'

				QMessageBox.critical(
					self.parent(), 'Error', error_message, QMessageBox.StandardButton.Ok
				)

		except Exception as e:
			# Handle any unexpected exceptions
			QMessageBox.critical(
				self.parent(),
				'Error',
				f'Unexpected error computing {component_name.lower()}: {str(e)}',
				QMessageBox.StandardButton.Ok,
			)

		# Update action states after computation attempt
		self.update_action_states()
