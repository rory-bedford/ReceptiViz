from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatusWidget(QWidget):
	"""Simple status widget showing three information bars for each data component."""

	def __init__(self, parent=None, data_manager=None):
		super().__init__(parent)
		self.data_manager = data_manager

		# Set up main layout
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setSpacing(0)  # No spacing between items

		# Create status bars
		self.activity_bar = ComponentStatusBar('Activity', self)

		# Create first separator with 30% transparency
		self.separator1 = QFrame()
		self.separator1.setFrameShape(QFrame.Shape.HLine)
		self.separator1.setFrameShadow(QFrame.Shadow.Plain)
		self.separator1.setStyleSheet(
			'background-color: rgba(204, 204, 204, 0.3); margin: 0px;'
		)
		self.separator1.setFixedHeight(1)

		self.stimulus_bar = ComponentStatusBar('Stimulus', self)

		# Create second separator with 30% transparency
		self.separator2 = QFrame()
		self.separator2.setFrameShape(QFrame.Shape.HLine)
		self.separator2.setFrameShadow(QFrame.Shadow.Plain)
		self.separator2.setStyleSheet(
			'background-color: rgba(204, 204, 204, 0.3); margin: 0px;'
		)
		self.separator2.setFixedHeight(1)

		self.rf_bar = ComponentStatusBar('Receptive Field', self)

		# Add status bars and separators to layout
		self.main_layout.addWidget(self.activity_bar)
		self.main_layout.addWidget(self.separator1)
		self.main_layout.addWidget(self.stimulus_bar)
		self.main_layout.addWidget(self.separator2)
		self.main_layout.addWidget(self.rf_bar)

		# Set height based on component heights
		total_height = (self.activity_bar.height() * 3) + 2  # 3 bars + 2 separators
		self.setFixedHeight(total_height)

		# Update initial status
		self.update_status()

	def update_status(self):
		"""Update status information for all components."""
		# Update Activity status
		activity = self.data_manager.activity

		# Build dimensions text
		info_parts = []
		if activity.timestamps is not None:
			info_parts.append(f'Timepoints: {activity.timestamps}')
		if activity.no_neurons is not None:
			info_parts.append(f'Neurons: {activity.no_neurons}')

		info_text = ' | '.join(info_parts)

		# Determine status and source
		is_available = activity.loaded or activity.computed
		source_text = ''
		if activity.computed:
			source_text = 'Computed'
		elif activity.loaded:
			source_text = str(activity.filepath)

		self.activity_bar.update_status(is_available, source_text, info_text)

		# Update Stimulus status
		stimulus = self.data_manager.stimulus

		# Build dimensions text
		info_parts = []
		if stimulus.timestamps is not None:
			info_parts.append(f'Timepoints: {stimulus.timestamps}')
		if stimulus.spatial_dims is not None:
			info_parts.append(f'Dims: {stimulus.spatial_dims}')

		info_text = ' | '.join(info_parts)

		# Determine status and source
		is_available = stimulus.loaded or stimulus.computed
		source_text = ''
		if stimulus.computed:
			source_text = 'Computed'
		elif stimulus.loaded:
			source_text = str(stimulus.filepath)

		self.stimulus_bar.update_status(is_available, source_text, info_text)

		# Update Receptive Field status
		rf = self.data_manager.receptive_field

		# Build dimensions text
		info_parts = []
		if rf.kernel_size is not None:
			info_parts.append(f'Kernel: {rf.kernel_size}')
		if rf.no_neurons is not None:
			info_parts.append(f'Neurons: {rf.no_neurons}')
		if rf.spatial_dims is not None:
			info_parts.append(f'Dims: {rf.spatial_dims}')

		info_text = ' | '.join(info_parts)

		# Determine status and source
		is_available = rf.loaded or rf.computed
		source_text = ''
		if rf.computed:
			source_text = 'Computed'
		elif rf.loaded:
			source_text = str(rf.filepath)

		self.rf_bar.update_status(is_available, source_text, info_text)


class ComponentStatusBar(QWidget):  # Changed back to QWidget
	"""A simple bar showing status information for a component."""

	def __init__(self, name, parent=None):
		super().__init__(parent)

		# Set up layout
		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(5, 8, 5, 8)  # Good padding for readability

		# Create name label with colon
		self.name_label = QLabel(f'{name}:')
		bold_font = QFont()
		bold_font.setBold(True)
		self.name_label.setFont(bold_font)
		self.name_label.setMinimumWidth(120)

		# Create green tick label
		self.tick_label = QLabel('✓')
		self.tick_label.setStyleSheet('color: green; font-weight: bold;')
		self.tick_label.setFixedWidth(15)

		# Create source label (filepath or "Computed")
		self.source_label = QLabel('')
		italic_font = QFont()
		italic_font.setItalic(True)
		self.source_label.setFont(italic_font)

		# Create dimensions info label
		self.info_label = QLabel('')
		self.info_label.setAlignment(Qt.AlignmentFlag.AlignRight)

		# Add to layout
		self.layout.addWidget(self.name_label)
		self.layout.addWidget(self.tick_label)
		self.layout.addWidget(self.source_label, 1)  # Stretch
		self.layout.addWidget(self.info_label)

		# Set fixed height
		self.setFixedHeight(28)

		# Initially hide the tick
		self.tick_label.setVisible(False)

	def update_status(self, is_available, source_text, info_text):
		"""Update the status bar information.

		Args:
			is_available: Whether the data is available (loaded or computed)
			source_text: Source information (filepath or 'Computed')
			info_text: Dimension information text
		"""
		# Show/hide the green tick based on availability
		self.tick_label.setVisible(is_available)

		# Update source and info text
		self.source_label.setText(source_text)
		self.info_label.setText(info_text)
