from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtCore import Qt

from receptual.processing.utils.download_sample_data import download_sample_data


class DownloadMenu(QMenu):
	"""Menu for sample data download operations."""

	def __init__(self, parent=None, data_manager=None):
		# Remove the ampersand from "Download" to eliminate the underline
		super().__init__('Download', parent)
		self.data_manager = data_manager
		self.parent_window = parent

		# Create action for downloading sample data
		self.download_sample_action = self.addAction('Download Sample Data')
		self.download_sample_action.triggered.connect(self.download_sample_data)

	def download_sample_data(self):
		"""Open a folder selector dialog and download sample data to the selected location."""
		# Show directory selection dialog
		folder_path = QFileDialog.getExistingDirectory(
			self.parent_window,
			'Select Folder to Download Sample Data',
			'',
			QFileDialog.Option.ShowDirsOnly,
		)

		# If user didn't cancel the dialog
		if folder_path:
			try:
				# Start the download with a progress dialog
				from PyQt6.QtWidgets import QProgressDialog
				from PyQt6.QtCore import QThread, pyqtSignal

				# Create a progress dialog
				progress = QProgressDialog(
					'Downloading sample data...', 'Cancel', 0, 0, self.parent_window
				)
				progress.setWindowModality(Qt.WindowModality.WindowModal)
				progress.setWindowTitle('Downloading')
				progress.setCancelButton(None)  # No cancel button
				progress.setAutoClose(True)
				progress.setMinimumDuration(0)  # Show immediately

				# Create a thread to download in the background
				class DownloadThread(QThread):
					finished = pyqtSignal(bool, str)

					def __init__(self, output_dir):
						super().__init__()
						self.output_dir = output_dir

					def run(self):
						try:
							result = download_sample_data(output_dir=self.output_dir)
							success = result is not None
							self.finished.emit(success, self.output_dir)
						except Exception as e:
							self.finished.emit(False, str(e))

				# Set up the download thread
				download_thread = DownloadThread(folder_path)
				download_thread.finished.connect(self.download_completed)
				download_thread.finished.connect(progress.close)

				# Start the download
				download_thread.start()
				progress.exec()

			except Exception as e:
				from PyQt6.QtWidgets import QMessageBox

				QMessageBox.critical(
					self.parent_window,
					'Download Error',
					f'Error downloading sample data: {str(e)}',
					QMessageBox.StandardButton.Ok,
				)

	def download_completed(self, success, message):
		"""Callback for when download is complete."""
		from PyQt6.QtWidgets import QMessageBox

		if success:
			QMessageBox.information(
				self.parent_window,
				'Download Complete',
				f'Sample data has been downloaded successfully to {message}',
				QMessageBox.StandardButton.Ok,
			)
		else:
			QMessageBox.critical(
				self.parent_window,
				'Download Failed',
				f'Failed to download sample data: {message}',
				QMessageBox.StandardButton.Ok,
			)
