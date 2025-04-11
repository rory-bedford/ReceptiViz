from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QMessageBox, 
                           QHBoxLayout, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt
from ..widgets.file_selection import FileSelectionWidget
from ..widgets.plot_widget import PlotWidget
from ..widgets.dimension_editor import DimensionEditorDialog
from ...processing.receptive_field import ReceptiveFieldProcessor

class ReceptiveFieldTab(QWidget):
    """Tab for receptive field analysis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the processor (shared between widgets)
        self.processor = ReceptiveFieldProcessor()
        
        # Set up main layout
        main_layout = QVBoxLayout(self)
        
        # File selectors and dimension editor section
        top_section_widget = QWidget()
        top_layout = QGridLayout(top_section_widget)
        top_layout.setColumnStretch(0, 6)  # File selectors get much more space
        top_layout.setColumnStretch(1, 1)  # Dimension editor gets minimal space
        
        # Create file selection widgets that use the processor for validation
        self.activity_selector = FileSelectionWidget("Activity Array:", "activity", self.processor)
        self.stimulus_selector = FileSelectionWidget("Stimulus Array:", "stimulus", self.processor)
        
        # Connect validation signals to update button state
        self.activity_selector.validation_changed.connect(self.update_button_state)
        self.stimulus_selector.validation_changed.connect(self.update_button_state)
        
        # Dimension editing button - taller to fill the height of both selectors
        self.dimension_button = QPushButton("Edit\nDimensions")
        self.dimension_button.setEnabled(False)
        self.dimension_button.clicked.connect(self.show_dimension_editor)
        self.dimension_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.dimension_button.setMaximumWidth(100)  # Restrict width
        
        # Add widgets to the top layout
        top_layout.addWidget(self.activity_selector, 0, 0)
        top_layout.addWidget(self.stimulus_selector, 1, 0)
        top_layout.addWidget(self.dimension_button, 0, 1, 2, 1)  # Span 2 rows
        
        # Plot widget container (initially empty)
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_container)
        self.plot_widget = None
        
        # Add widgets to main layout
        main_layout.addWidget(top_section_widget)
        main_layout.addWidget(self.plot_container, 1)  # Give plot container the stretch priority
        
        # Plot button at the absolute bottom
        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.generate_plot)
        self.plot_button.setMinimumWidth(200)  # Make it reasonably wide
        self.plot_button.setMinimumHeight(40)  # Make it a bit taller for better visibility
        
        # Add the plot button directly to the main layout at the end
        main_layout.addWidget(self.plot_button, 0, Qt.AlignmentFlag.AlignCenter)
        
    def update_button_state(self, _=None):
        """Update the state of the buttons based on file validity"""
        activity_valid = self.activity_selector.is_valid_file()
        stimulus_valid = self.stimulus_selector.is_valid_file()
        
        self.plot_button.setEnabled(activity_valid and stimulus_valid)
        self.dimension_button.setEnabled(activity_valid or stimulus_valid)
        
    def show_dimension_editor(self):
        """Show unified dimension editor dialog"""
        # Only show if at least one file is valid
        if not self.activity_selector.is_valid_file() and not self.stimulus_selector.is_valid_file():
            return
            
        editor_dialog = DimensionEditorDialog(self.processor, self)
        if editor_dialog.exec():
            # Update dimension info display in both selectors
            self.activity_selector.update_dimension_info()
            self.stimulus_selector.update_dimension_info()
        
    def generate_plot(self):
        """Generate the plot using the processor"""
        try:
            # Validate compatibility between arrays
            self.processor.validate_compatibility()
            
            if self.processor.get_errors():
                self.show_error("Validation Error", "\n".join(self.processor.get_errors()))
                return
                
            # Process the data
            self.processor.process()
            
            if self.processor.get_errors():
                self.show_error("Processing Error", "\n".join(self.processor.get_errors()))
                return
                
            # Get the result
            result = self.processor.get_result()
            
            # Update the plot
            if self.plot_widget:
                self.plot_layout.removeWidget(self.plot_widget)
                self.plot_widget.deleteLater()
                
            self.plot_widget = PlotWidget(self.processor)
            self.plot_layout.addWidget(self.plot_widget)
            
        except Exception as e:
            self.show_error("Error", str(e))
            
    def show_error(self, title, message):
        """Show an error message"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
