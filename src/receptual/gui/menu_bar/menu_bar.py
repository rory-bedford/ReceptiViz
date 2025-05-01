from PyQt6.QtWidgets import QMenuBar

from receptual.gui.menu_bar.load_menu import LoadMenu
from receptual.gui.menu_bar.compute_menu import ComputeMenu
from receptual.gui.menu_bar.save_menu import SaveMenu
from receptual.gui.menu_bar.plot_menu import PlotMenu
from receptual.gui.menu_bar.download_menu import DownloadMenu  # Add the new menu


class MenuBar(QMenuBar):
	"""Main menu bar for the application.

	Organizes the File, Load, Compute, Save, Plot, and Download menus.
	"""

	def __init__(self, parent=None, data_manager=None):
		super().__init__(parent)

		self.data_manager = data_manager
		self.main_window = parent

		# Create and add the menus
		self.load_menu = LoadMenu(self.main_window, data_manager)
		self.addMenu(self.load_menu)

		self.compute_menu = ComputeMenu(self.main_window, data_manager)
		self.addMenu(self.compute_menu)

		self.save_menu = SaveMenu(self.main_window, data_manager)
		self.addMenu(self.save_menu)

		self.plot_menu = PlotMenu(self.main_window, data_manager)
		self.addMenu(self.plot_menu)

		# Add our new download menu
		self.download_menu = DownloadMenu(self.main_window, data_manager)
		self.addMenu(self.download_menu)
