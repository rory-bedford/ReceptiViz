from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .tabs.receptive_field_tab import ReceptiveFieldTab

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ReceptiViz")
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.receptive_field_tab = ReceptiveFieldTab()
        self.encoding_tab = QWidget()
        self.decoding_tab = QWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.receptive_field_tab, "Receptive Field")
        self.tab_widget.addTab(self.encoding_tab, "Encoding")
        self.tab_widget.addTab(self.decoding_tab, "Decoding")
        
        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)

