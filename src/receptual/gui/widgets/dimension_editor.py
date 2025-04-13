from PyQt6.QtWidgets import (
	QDialog,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QPushButton,
	QLineEdit,
	QTabWidget,
	QWidget,
	QFormLayout,
	QDoubleSpinBox,
)


class DimensionEditorDialog(QDialog):
	"""Dialog for editing dimension names and units"""

	def __init__(self, processor, parent=None):
		super().__init__(parent)
		self.processor = processor
		self.setWindowTitle('Edit Dimensions')
		self.setMinimumWidth(400)

		# Set up main layout
		layout = QVBoxLayout(self)

		# Create tab widget
		self.tab_widget = QTabWidget()

		# Create tabs for activity, stimulus, and time settings
		self.activity_tab = self._create_activity_tab()
		self.stimulus_tab = self._create_stimulus_tab()
		self.time_tab = (
			self._create_time_tab()
		)  # New tab specifically for time settings

		# Add tabs
		self.tab_widget.addTab(self.activity_tab, 'Activity')
		self.tab_widget.addTab(self.stimulus_tab, 'Stimulus')
		self.tab_widget.addTab(self.time_tab, 'Time Settings')  # Add time settings tab

		# Add tab widget to main layout
		layout.addWidget(self.tab_widget)

		# Create buttons
		button_layout = QHBoxLayout()
		self.ok_button = QPushButton('OK')
		self.cancel_button = QPushButton('Cancel')

		# Connect button signals
		self.ok_button.clicked.connect(self.accept)
		self.cancel_button.clicked.connect(self.reject)

		# Add buttons to layout
		button_layout.addStretch()
		button_layout.addWidget(self.ok_button)
		button_layout.addWidget(self.cancel_button)

		# Add button layout to main layout
		layout.addLayout(button_layout)

		# Initialize with current settings
		self._initialize_fields()

	def _create_activity_tab(self):
		"""Create the activity tab content"""
		tab = QWidget()
		layout = QFormLayout(tab)

		# Get activity array info
		dim_info = self.processor.get_dimension_info('activity')
		self.processor.get_value_info('activity')

		# Check if activity is loaded
		if not dim_info or self.processor.activity is None:
			layout.addRow(QLabel('No activity array loaded'))
			return tab

		# Add activity value name and unit
		self.activity_value_name = QLineEdit()
		self.activity_value_unit = QLineEdit()
		layout.addRow('Value Name:', self.activity_value_name)
		layout.addRow('Value Unit:', self.activity_value_unit)

		return tab

	def _create_stimulus_tab(self):
		"""Create the stimulus tab content"""
		tab = QWidget()
		layout = QFormLayout(tab)

		# Get stimulus array info
		dim_info = self.processor.get_dimension_info('stimulus')
		self.processor.get_value_info('stimulus')

		# Check if stimulus is loaded
		if not dim_info or self.processor.stimulus is None:
			layout.addRow(QLabel('No stimulus array loaded'))
			return tab

		# Add stimulus value name and unit
		self.stimulus_value_name = QLineEdit()
		self.stimulus_value_unit = QLineEdit()
		layout.addRow('Value Name:', self.stimulus_value_name)
		layout.addRow('Value Unit:', self.stimulus_value_unit)

		# Add fields for each dimension (except time dimension)
		self.stim_dim_names = []
		self.stim_dim_units = []

		for i, _name in enumerate(dim_info.get('dims', [])):
			if i == 0:  # Skip time dimension (handled in time tab)
				continue

			# Create fields for dimension name and unit
			name_field = QLineEdit()
			self.stim_dim_names.append(name_field)

			unit_field = QLineEdit()
			self.stim_dim_units.append(unit_field)

			# Format the dimension label with its shape
			if 'shape' in dim_info and i < len(dim_info['shape']):
				dim_label = f'Dimension {i} ({dim_info["shape"][i]} points):'
			else:
				dim_label = f'Dimension {i}:'

			# Add fields to layout
			layout.addRow(f'{dim_label} Name', name_field)
			layout.addRow(f'{dim_label} Unit', unit_field)

		return tab

	def _create_time_tab(self):
		"""Create the time settings tab specifically for sample rate"""
		tab = QWidget()
		layout = QFormLayout(tab)

		# Add sample rate spinbox
		self.sample_rate_spinbox = QDoubleSpinBox()
		self.sample_rate_spinbox.setRange(0.1, 10000.0)  # 0.1 Hz to 10 kHz
		self.sample_rate_spinbox.setSingleStep(1.0)
		self.sample_rate_spinbox.setValue(self.processor.get_sample_rate())
		self.sample_rate_spinbox.setSuffix(' Hz')
		self.sample_rate_spinbox.setDecimals(1)

		# Add labels with explanations
		layout.addRow(QLabel('<b>Time Dimensions</b>'))
		layout.addRow(QLabel('Set the sample rate to convert from frames to seconds'))
		layout.addRow('Sample Rate:', self.sample_rate_spinbox)

		# Show the current time settings
		current_rate = self.processor.get_sample_rate()
		example_frames = [10, 100, 1000]
		examples_text = 'Examples:\n'
		for frame in example_frames:
			time = frame / current_rate
			unit = 'ms' if time < 1 else 's'
			time_val = time * 1000 if time < 1 else time
			examples_text += f'• Frame {frame} = {time_val:.1f} {unit}\n'

		examples_label = QLabel(examples_text)
		examples_label.setWordWrap(True)
		layout.addRow(examples_label)

		# Add a note about implications
		note_label = QLabel(
			'Note: All time values will be displayed in seconds in plots. '
			'Time values are calculated as (frame index / sample rate).'
		)
		note_label.setWordWrap(True)
		note_label.setStyleSheet('font-style: italic; color: gray;')
		layout.addRow(note_label)

		# Connect sample rate changes to update examples
		self.sample_rate_spinbox.valueChanged.connect(
			lambda rate: self._update_time_examples(
				examples_label, rate, example_frames
			)
		)

		return tab

	def _update_time_examples(self, label, rate, frames):
		"""Update the time examples when sample rate changes"""
		examples_text = 'Examples:\n'
		for frame in frames:
			time = frame / rate
			unit = 'ms' if time < 1 else 's'
			time_val = time * 1000 if time < 1 else time
			examples_text += f'• Frame {frame} = {time_val:.1f} {unit}\n'
		label.setText(examples_text)

	def _initialize_fields(self):
		"""Initialize form fields with current values"""
		# Activity value info
		activity_value_info = self.processor.get_value_info('activity')
		if activity_value_info and hasattr(self, 'activity_value_name'):
			self.activity_value_name.setText(
				activity_value_info.get('name', 'Firing rate')
			)
			self.activity_value_unit.setText(activity_value_info.get('unit', 'Hz'))

		# Stimulus value info
		stimulus_value_info = self.processor.get_value_info('stimulus')
		if stimulus_value_info and hasattr(self, 'stimulus_value_name'):
			self.stimulus_value_name.setText(
				stimulus_value_info.get('name', 'Stimulus')
			)
			self.stimulus_value_unit.setText(stimulus_value_info.get('unit', 'a.u.'))

		# Stimulus dimension info
		dim_info = self.processor.get_dimension_info('stimulus')
		if dim_info:
			# Fill dimension fields
			for i in range(len(self.stim_dim_names)):
				dim_idx = i + 1  # Skip time dimension
				if dim_idx < len(dim_info.get('dims', [])):
					self.stim_dim_names[i].setText(dim_info['dims'][dim_idx])
				if dim_idx < len(dim_info.get('units', [])):
					self.stim_dim_units[i].setText(dim_info['units'][dim_idx])

	def accept(self):
		"""Accept changes and update processor settings"""
		# Update activity value info
		if hasattr(self, 'activity_value_name'):
			self.processor.set_value_info(
				'activity',
				self.activity_value_name.text(),
				self.activity_value_unit.text(),
			)

		# Update stimulus value info
		if hasattr(self, 'stimulus_value_name'):
			self.processor.set_value_info(
				'stimulus',
				self.stimulus_value_name.text(),
				self.stimulus_value_unit.text(),
			)

		# Update stimulus dimension info
		dim_info = self.processor.get_dimension_info('stimulus')
		if dim_info:
			new_dim_names = dim_info.get('dims', [])[:]  # Copy current names
			new_dim_units = dim_info.get('units', [])[:]  # Copy current units

			# Update non-time dimensions
			for i, name_field in enumerate(self.stim_dim_names):
				dim_idx = i + 1  # Skip time dimension (0)
				if dim_idx < len(new_dim_names):
					new_dim_names[dim_idx] = name_field.text()

			for i, unit_field in enumerate(self.stim_dim_units):
				dim_idx = i + 1  # Skip time dimension (0)
				if dim_idx < len(new_dim_units):
					new_dim_units[dim_idx] = unit_field.text()

			# Update dimension info with new names and units
			self.processor.set_dimension_info('stimulus', new_dim_names, new_dim_units)

		# Update sample rate
		sample_rate = self.sample_rate_spinbox.value()
		self.processor.set_sample_rate(sample_rate)

		# Call parent's accept method
		super().accept()
