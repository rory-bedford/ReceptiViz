from PyQt6.QtWidgets import (
	QWidget,
	QHBoxLayout,
	QPushButton,
	QLabel,
	QFileDialog,
	QStyle,
	QSizePolicy,
	QSpinBox,  # Add this import
)
from PyQt6.QtCore import pyqtSignal, Qt


class FileSelector(QWidget):
	"""Widget for selecting data files with a label and buttons.

	This widget displays the name of the data array, a button to select a file,
	and a button to reset the selection.

	Attributes:
		array_manager: Reference to the data array manager (Activity, Stimulus, or ReceptiveField)
		file_selected: Signal emitted when a file is successfully selected
		reset_clicked: Signal emitted when the reset button is clicked
		data_changed: Signal emitted when the array data changes (selected, reset, or computed)
		kernel_size_changed: Signal emitted when the kernel size changes
	"""

	file_selected = pyqtSignal(str)
	reset_clicked = pyqtSignal()
	data_changed = pyqtSignal()  # New signal for data changes
	kernel_size_changed = pyqtSignal(int)  # Add new signal for kernel size changes

	def __init__(self, array_manager, parent=None):
		super().__init__(parent)
		self.array_manager = array_manager
		self.init_ui()

	def init_ui(self):
		"""Initialize the UI components"""
		# Create layout
		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)

		# Create a container widget for the labels
		label_container = QWidget()
		label_layout = QHBoxLayout(label_container)
		label_layout.setContentsMargins(0, 0, 0, 0)

		# Add main label for array name (left-aligned)
		self.name_label = QLabel(self.array_manager.name)
		self.name_label.setSizePolicy(
			QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
		)
		label_layout.addWidget(self.name_label)

		# Add info label for details (right-aligned)
		self.info_label = QLabel()
		self.info_label.setAlignment(
			Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
		)
		label_layout.addWidget(self.info_label)

		# Add the label container to the main layout
		layout.addWidget(label_container, 1)  # Give it stretch factor of 1

		# Create the kernel size widget (initially hidden)
		self.kernel_widget = QWidget()
		kernel_layout = QHBoxLayout(self.kernel_widget)
		kernel_layout.setContentsMargins(0, 0, 0, 0)

		kernel_label = QLabel('Kernel:')
		kernel_layout.addWidget(kernel_label)

		self.kernel_spin = QSpinBox()
		self.kernel_spin.setRange(1, 100)  # Set appropriate range
		self.kernel_spin.setValue(10)  # Default value
		self.kernel_spin.valueChanged.connect(self.on_kernel_size_changed)
		kernel_layout.addWidget(self.kernel_spin)

		layout.addWidget(self.kernel_widget)
		self.kernel_widget.setVisible(False)  # Hide initially

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

		# Set the initial visibility state
		self._update_widget_visibility()

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
		self._update_widget_visibility()  # Update visibility when data changes
		self.data_changed.emit()

	def on_kernel_size_changed(self, value):
		"""Handle kernel size changes"""
		if hasattr(self.array_manager, 'update_kernel_size'):
			try:
				# Use the manager's update_kernel_size method instead of direct property assignment
				self.array_manager.update_kernel_size(value)
				# Emit signals
				self.kernel_size_changed.emit(value)
				self.data_changed.emit()
			except Exception as e:
				# Show error if kernel size update fails
				from PyQt6.QtWidgets import QMessageBox

				QMessageBox.critical(
					self, 'Kernel Size Error', f'Error updating kernel size: {str(e)}'
				)
				# Reset spin box to current kernel size
				if hasattr(self.array_manager, 'kernel_size'):
					self.kernel_spin.setValue(self.array_manager.kernel_size)

	def _update_label(self):
		"""Update the labels to show file information"""
		# Main label shows name and primary info
		if self.array_manager.loaded:
			self.name_label.setText(
				f'{self.array_manager.name}: {self.array_manager.filepath}'
			)
		elif hasattr(self.array_manager, 'computed') and self.array_manager.computed:
			self.name_label.setText(f'{self.array_manager.name}: Computed')
		else:
			self.name_label.setText(self.array_manager.name)

		# Info label shows additional details (right-aligned)
		info_parts = []
		if hasattr(self.array_manager, 'timestamps') and self.array_manager.timestamps:
			info_parts.append(f'Timestamps: {self.array_manager.timestamps}')
		if (
			hasattr(self.array_manager, 'kernel_size')
			and self.array_manager.kernel_size
		):
			info_parts.append(f'Kernel: {self.array_manager.kernel_size}')
		if hasattr(self.array_manager, 'no_neurons') and self.array_manager.no_neurons:
			info_parts.append(f'Neurons: {self.array_manager.no_neurons}')
		if (
			hasattr(self.array_manager, 'spatial_dims')
			and self.array_manager.spatial_dims
		):
			info_parts.append(f'Dims: {self.array_manager.spatial_dims}')

		self.info_label.setText(' | '.join(info_parts))

	def update_status(self):
		"""Update the widget status based on array_manager state"""
		# Enable/disable buttons based on availability and loading state
		self.select_button.setEnabled(self.array_manager.available)
		self.reset_button.setEnabled(self.array_manager.loaded)

		# Update label text
		self._update_label()

		# Update widget visibility
		self._update_widget_visibility()

	def _update_widget_visibility(self):
		"""Update visibility of widgets based on manager state"""
		is_rf = self.array_manager.name == 'Receptive Field'
		is_computed = (
			hasattr(self.array_manager, 'computed') and self.array_manager.computed
		)

		# Show kernel size widget for computed RF
		if is_rf and is_computed:
			self.kernel_widget.setVisible(True)
			self.select_button.setVisible(False)
			# Set the current kernel size if available
			if (
				hasattr(self.array_manager, 'kernel_size')
				and self.array_manager.kernel_size
			):
				self.kernel_spin.setValue(self.array_manager.kernel_size)
		else:
			self.kernel_widget.setVisible(False)
			self.select_button.setVisible(True)
