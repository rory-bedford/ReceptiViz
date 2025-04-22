from PyQt6.QtWidgets import (
	QWidget,
)
from receptual.processing.data_manager import EncoderDataManager


class EncoderTab(QWidget):
	"""Tab for receptive field analysis"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.processor = EncoderDataManager()
