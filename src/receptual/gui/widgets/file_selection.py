from PyQt6.QtWidgets import (
	QWidget,
	QPushButton,
	QLabel,
	QHBoxLayout,
	QVBoxLayout,
	QFileDialog,
	QMessageBox,
	QToolTip,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette, QFont


class FileSelectionWidget(QWidget):
	"""Self-contained widget for selecting and validating files"""

	# Signal when file validation status changes
	validation_changed = pyqtSignal(bool)
	# Signal for when a file is selected - now passes the file path
	file_selected = pyqtSignal(str)

	def __init__(self, label_text, file_type, processor, parent=None):
		super().__init__(parent)
		self.label_text = label_text
		self.file_type = file_type  # "activity", "stimulus" or "receptive_field"
		self.processor = processor  # Reference to the processor for validation
		self.selected_file = None
		self.is_valid = False
		self.validation_message = ''

		# Set up UI
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)

		# File selection row
		file_row = QHBoxLayout()
		self.label = QLabel(label_text)
		self.file_path_label = QLabel('No file selected')
		self.file_path_label.setToolTip('No file selected')

		# Add dimension info label - inline with filepath
		self.dimension_info_label = QLabel()
		italic_font = QFont()
		italic_font.setItalic(True)
		self.dimension_info_label.setFont(italic_font)
		self.dimension_info_label.setStyleSheet('color: gray;')

		self.status_label = QLabel('')
		self.status_label.setCursor(Qt.CursorShape.WhatsThisCursor)
		self.status_label.setToolTip('No file selected')

		self.select_button = QPushButton('Select File')

		# Put everything in the file row
		file_row.addWidget(self.label)
		file_row.addWidget(self.file_path_label)
		file_row.addWidget(
			self.dimension_info_label, 1
		)  # Give stretch to dimension info
		file_row.addWidget(self.status_label)
		file_row.addWidget(self.select_button)

		main_layout.addLayout(file_row)

		# Connect signals
		self.select_button.clicked.connect(self.select_file)
		self.status_label.mousePressEvent = self.show_status_message

	def select_file(self):
		"""Show file dialog and handle selection"""
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			f'Select {self.label_text}',
			'',
			'NumPy Files (*.npy);;All Files (*.*)',
		)

		if file_path:
			self.selected_file = file_path
			self.file_path_label.setText(
				file_path.split('/')[-1]
			)  # Show just the filename
			self.file_path_label.setToolTip(file_path)  # Full path on hover

			# Clear processor errors before validation
			self.processor.clear_errors()

			# Emit the file_selected signal - validation will be handled by EncoderTab
			self.file_selected.emit(file_path)

			# We'll assume the file becomes valid after selection, later the results
			# will be passed to our update methods from the EncoderTab

	def update_dimension_info(self):
		"""Update the dimension info display based on current processor state"""
		if self.file_type == 'activity' and self.processor.activity is None:
			self.dimension_info_label.setText('')
			self.is_valid = False
			self.update_status(False)
			return
		elif self.file_type == 'stimulus' and self.processor.stimulus is None:
			self.dimension_info_label.setText('')
			self.is_valid = False
			self.update_status(False)
			return
		elif (
			self.file_type == 'receptive_field'
			and self.processor.receptive_field is None
		):
			self.dimension_info_label.setText('')
			self.is_valid = False
			self.update_status(False)
			return

		# Get array shape based on file type
		shape = None
		if self.file_type == 'activity':
			shape = self.processor.activity.shape
			self.is_valid = True
		elif self.file_type == 'stimulus':
			shape = self.processor.stimulus.shape
			self.is_valid = True
		elif self.file_type == 'receptive_field':
			shape = self.processor.receptive_field.shape
			self.is_valid = True

		if shape is None:
			self.dimension_info_label.setText('')
			return

		# The array is valid at this point, update status
		self.update_status(True)

		# Get dimension information
		dim_info = self.processor.get_dimension_info(self.file_type)
		if not dim_info:
			self.dimension_info_label.setText('')
			return

		dim_names = dim_info.get('dims', [])
		dim_units = dim_info.get('units', [])

		# Create formatted dimension string
		dim_strings = []
		sample_rate = self.processor.get_sample_rate()

		for i in range(len(shape)):
			name = dim_names[i] if i < len(dim_names) else f'dim_{i}'
			unit = dim_units[i] if i < len(dim_units) else ''
			unit_str = f' ({unit})' if unit else ''

			# For time dimension, always show duration in seconds
			if i == 0 and name.lower() == 'time' and unit == 's':
				# Calculate duration in seconds directly
				total_time = shape[i] / sample_rate

				# Format with appropriate precision
				time_format = '{:.2f}' if total_time < 1 else '{:.1f}'
				time_str = time_format.format(total_time)

				# Show duration in seconds
				dim_strings.append(
					f'{name}{unit_str}: {time_str}s ({shape[i]} samples)'
				)
			else:
				# For non-time dimensions, show size directly
				dim_strings.append(f'{name}{unit_str}: {shape[i]}')

		# Add value info
		value_info = self.processor.get_value_info(self.file_type)
		if value_info:
			value_str = f'{value_info.get("name", "")} ({value_info.get("unit", "")})'
			self.dimension_info_label.setText(
				' × '.join(dim_strings) + f'   {value_str}'
			)
		else:
			self.dimension_info_label.setText(' × '.join(dim_strings))

	def update_status(self, is_valid, message=None):
		"""Update the status indicator"""
		if message is not None:
			self.validation_message = message

		self.is_valid = is_valid
		palette = self.status_label.palette()

		if is_valid:
			palette.setColor(QPalette.ColorRole.WindowText, QColor('green'))
			self.status_label.setText('✓')
			if not self.validation_message:
				self.validation_message = f'Success! Valid {self.file_type} array.'

			self.status_label.setToolTip(self.validation_message)
		else:
			palette.setColor(QPalette.ColorRole.WindowText, QColor('red'))
			self.status_label.setText('✗')
			if not self.validation_message:
				self.validation_message = 'Invalid file'

			self.status_label.setToolTip(self.validation_message)

		self.status_label.setPalette(palette)
		self.validation_changed.emit(is_valid)

	def set_success(self, message=None):
		"""Set the widget to success state with optional message"""
		if message:
			self.validation_message = message
		else:
			self.validation_message = f'Success! Valid {self.file_type} array.'

		self.update_status(True)
		self.show_success()

	def set_error(self, message):
		"""Set the widget to error state with the given message"""
		self.validation_message = message
		self.update_status(False)
		self.show_error(message)

	def show_error(self, message):
		"""Show error message"""
		msg_box = QMessageBox(self)
		msg_box.setIcon(QMessageBox.Icon.Critical)
		msg_box.setWindowTitle('Validation Error')
		msg_box.setText(message)
		msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
		msg_box.exec()

	def show_success(self):
		"""Show success message"""
		QToolTip.showText(
			self.mapToGlobal(self.status_label.pos()),
			'Success! File validated successfully.',
			self,
			self.status_label.rect(),
			2000,  # Hide after 2 seconds
		)

	def show_status_message(self, event):
		"""Show status message when clicking on status label"""
		if self.validation_message:
			if self.is_valid:
				QMessageBox.information(
					self, 'Validation Success', self.validation_message
				)
			else:
				QMessageBox.critical(self, 'Validation Error', self.validation_message)

	def is_valid_file(self):
		"""Return if the file is valid"""
		# Determine validity based on processor state
		if self.file_type == 'activity':
			return self.processor.activity is not None
		elif self.file_type == 'stimulus':
			return self.processor.stimulus is not None
		elif self.file_type == 'receptive_field':
			return self.processor.receptive_field is not None
		return False
