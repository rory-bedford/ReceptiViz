from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotWidget(QWidget):
    def __init__(self, array: np.ndarray, parent=None):
        super().__init__(parent)
        self.array = array
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self._plot_array()

    def _plot_array(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.array, linestyle='-', marker='o', markersize=4)
        ax.set_title("NumPy Array Visualization")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.grid(True)
        self.canvas.draw()

