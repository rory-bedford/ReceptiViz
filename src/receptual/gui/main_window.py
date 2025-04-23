from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from receptual.gui.tabs.encoder import EncoderTab
from receptual.processing.data_manager import EncoderDataManager


class MainWindow(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle('Receptual')

		# Create main layout
		layout = QVBoxLayout(self)

		# Initialize data managers
		self.encoder_data_manager = EncoderDataManager()

		# Create tab widget
		self.tab_widget = QTabWidget()

		# Create tabs
		self.encoding_tab = EncoderTab(data_manager=self.encoder_data_manager)
		self.decoding_tab = QWidget()

		# Add tabs to tab widget
		self.tab_widget.addTab(self.encoding_tab, 'Encoding')
		self.tab_widget.addTab(self.decoding_tab, 'Decoding')

		# Add tab widget to main layout
		layout.addWidget(self.tab_widget)
