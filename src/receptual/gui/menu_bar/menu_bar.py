from PyQt6.QtWidgets import QMenuBar

from receptual.gui.menu_bar.load_menu import LoadMenu
from receptual.gui.menu_bar.compute_menu import ComputeMenu
from receptual.gui.menu_bar.save_menu import SaveMenu
from receptual.gui.menu_bar.plot_menu import PlotMenu


class MenuBar(QMenuBar):
	"""Main menu bar for the application.

	Organizes the Load, Compute, Save and Plot menus.
	"""

	def __init__(self, parent=None, data_manager=None):
		super().__init__(parent)

		self.data_manager = data_manager
		self.main_window = parent

		# Create and add the menus
		self.load_menu = LoadMenu(self, data_manager)
		self.compute_menu = ComputeMenu(self, data_manager)
		self.save_menu = SaveMenu(self, data_manager)
		self.plot_menu = PlotMenu(
			self.main_window, data_manager
		)  # Pass the main window directly

		# Add menus to the menu bar
		self.addMenu(self.load_menu)
		self.addMenu(self.compute_menu)
		self.addMenu(self.save_menu)
		self.addMenu(self.plot_menu)
