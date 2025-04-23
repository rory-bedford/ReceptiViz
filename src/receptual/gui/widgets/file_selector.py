from PyQt6.QtWidgets import (
	QWidget,
	QHBoxLayout,
	QPushButton,
	QLabel,
	QFileDialog,
	QStyle,
	QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal


class FileSelector(QWidget):
	"""Widget for selecting data files with a label and buttons.

	This widget displays the name of the data array, a button to select a file,
	and a button to reset the selection.

	Attributes:
		array_manager: Reference to the data array manager (Activity, Stimulus, or ReceptiveField)
		file_selected: Signal emitted when a file is successfully selected
		reset_clicked: Signal emitted when the reset button is clicked
		data_changed: Signal emitted when the array data changes (selected, reset, or computed)
	"""

	file_selected = pyqtSignal(str)
	reset_clicked = pyqtSignal()
	data_changed = pyqtSignal()  # New signal for data changes

	def __init__(self, array_manager, parent=None):
		super().__init__(parent)
		self.array_manager = array_manager
		self.init_ui()

	def init_ui(self):
		"""Initialize the UI components"""
		# Create layout
		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)

		# Add label for array name
		self.name_label = QLabel(self.array_manager.name)
		self.name_label.setSizePolicy(
			QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
		)
		layout.addWidget(self.name_label)

		# Add the Select File button
		self.select_button = QPushButton('Select File')
		# Use folder icon if available
		icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
		self.select_button.setIcon(icon)
		self.select_button.clicked.connect(self.select_file)
		# Only enabled if the array_manager is available for selection
		self.select_button.setEnabled(self.array_manager.available)
		layout.addWidget(self.select_button)

		# Add the Reset button
		self.reset_button = QPushButton('Reset')
		# Use clear/delete icon if available
		icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
		self.reset_button.setIcon(icon)
		self.reset_button.clicked.connect(self.reset_data)
		# Only enabled if data IS loaded
		self.reset_button.setEnabled(self.array_manager.loaded)
		layout.addWidget(self.reset_button)

	def select_file(self):
		# Start in last directory if file was previously selected
		start_dir = ''
		if (
			hasattr(self.array_manager, 'filepath')
			and self.array_manager.filepath is not None
		):
			start_dir = str(self.array_manager.filepath.parent)

		file_path, _ = QFileDialog.getOpenFileName(
			self,
			f'Select {self.array_manager.name} File',
			start_dir,
			'NumPy Files (*.npy);;All Files (*)',
		)

		if file_path:
			# Attempt to set the data in the array manager
			success = self.array_manager.set_data(file_path)

			if success:
				# Enable reset button once we have loaded data
				self.reset_button.setEnabled(True)
				# Update select button based on availability
				self.select_button.setEnabled(self.array_manager.available)
				# Show file name in the label
				self._update_label()
				# Emit signals that file was selected and data changed
				self.file_selected.emit(file_path)
				self.data_changed.emit()  # emit data changed signal
			else:
				# Show error message
				from PyQt6.QtWidgets import QMessageBox

				error_msg = '\n'.join(self.array_manager.errors)
				QMessageBox.critical(
					self,
					'Data Error',
					f'Error loading {self.array_manager.name} data:\n{error_msg}',
				)
				# Clear errors after displaying
				self.array_manager.errors = []

	def reset_data(self):
		"""Reset the data in the array manager"""
		self.array_manager.reset_state()
		self.name_label.setText(self.array_manager.name)
		self.reset_button.setEnabled(False)
		self.select_button.setEnabled(self.array_manager.available)
		self.reset_clicked.emit()
		self.data_changed.emit()  # emit data changed signal

	def notify_data_changed(self):
		"""Call this when the array manager's data changes outside the widget"""
		self.update_status()
		self.data_changed.emit()

	def _update_label(self):
		"""Update the label to show file information"""
		if self.array_manager.loaded:
			text = f'{self.array_manager.name}: {self.array_manager.filepath}'
		elif hasattr(self.array_manager, 'computed') and self.array_manager.computed:
			text = f'{self.array_manager.name}: Computed'
		else:
			text = self.array_manager.name
		if hasattr(self.array_manager, 'timestamps'):
			text += f' (Timestamps: {self.array_manager.timestamps})'
		if hasattr(self.array_manager, 'kernel_size'):
			text += f' (Kernel Size: {self.array_manager.kernel_size})'
		if hasattr(self.array_manager, 'no_neurons'):
			text += f' (Neurons: {self.array_manager.no_neurons})'
		if hasattr(self.array_manager, 'spatial_dims'):
			text += f' (Spatial Dims: {self.array_manager.spatial_dims})'
		self.name_label.setText(text)

	def update_status(self):
		"""Update the widget status based on array_manager state"""
		# Enable/disable buttons based on availability and loading state
		self.select_button.setEnabled(self.array_manager.available)
		self.reset_button.setEnabled(self.array_manager.loaded)

		# Update label text
		self._update_label()
