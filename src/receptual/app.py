import sys
from PyQt6.QtWidgets import QApplication
from receptual.gui.main_window import MainWindow


def main():
	app = QApplication(sys.argv)
	window = MainWindow()
	window.showMaximized()  # Shows the window maximized (full screen without hiding taskbar)
	# Alternatively, use window.showFullScreen() to completely cover the screen
	sys.exit(app.exec())
